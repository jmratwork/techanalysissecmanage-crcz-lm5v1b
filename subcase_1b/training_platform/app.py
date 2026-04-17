import os
import uuid
import time
import threading
import subprocess
import tempfile
import shutil
from functools import wraps
from flask import Flask, request, jsonify, g

import phishing_quiz
from open_edx_client import OpenEdXClient
from results_service import append_result, aggregate_results
from security import hash_password, verify_password
from storage import (
    TRAINING_DB_PATH,
    create_session,
    create_user,
    get_session_by_token,
    get_user,
    init_schema,
    revoke_session,
)

app = Flask(__name__)

# In-memory stores
courses = {}  # course_id -> {title, content, instructor}
invites = {}  # invite_code -> {course_id, email}
progress = {}  # (course_id, username) -> progress
quiz_results = {}  # (course_id, username) -> {answers, score}
edx_failures = []  # list of Open edX reporting failures
jobs = {}  # job_id -> {status, tool, output}

open_edx = OpenEdXClient()

# Default subnet for KYPO exercises; can be overridden with environment variable
KYPO_SUBNET = os.getenv('KYPO_SUBNET', '10.10.0.0/24')
KYPO_TARGET_HOST = os.getenv('KYPO_TARGET_HOST', 'http://localhost')
OPENVAS_TARGET_HOST = os.getenv('OPENVAS_TARGET_HOST', KYPO_SUBNET)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CALDERA_PROFILE = os.path.join(BASE_DIR, '..', 'caldera_profiles', 'discovery.json')
ZAP_CONFIG = os.path.join(BASE_DIR, '..', 'zap_baseline.conf')
OPENVAS_TEMPLATE = os.path.join(BASE_DIR, '..', 'openvas_task_template.xml')


def _prepare_template(path):
    """Return path to a temporary file with environment substitutions."""

    with open(path, 'r', encoding='utf-8') as fh:
        content = fh.read()
    content = content.replace('KYPO_SUBNET', KYPO_SUBNET)
    content = content.replace('OPENVAS_TARGET_HOST', OPENVAS_TARGET_HOST)
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.write(content.encode('utf-8'))
    tmp.close()
    return tmp.name


ZAP_CONF = _prepare_template(ZAP_CONFIG)
CALDERA_PROFILE_PATH = _prepare_template(CALDERA_PROFILE)
with open(OPENVAS_TEMPLATE, 'r', encoding='utf-8') as fh:
    OPENVAS_XML = fh.read()
OPENVAS_XML = OPENVAS_XML.replace('KYPO_SUBNET', KYPO_SUBNET)
OPENVAS_XML = OPENVAS_XML.replace('OPENVAS_TARGET_HOST', OPENVAS_TARGET_HOST)

SESSION_TTL_SECONDS = int(os.getenv('SESSION_TTL_SECONDS', '3600'))


COMMANDS = {
    'nmap': ['nmap', '-sV', KYPO_SUBNET],
    'zap': ['zap-baseline.py', '-t', KYPO_TARGET_HOST, '-c', ZAP_CONF],
    'caldera': ['caldera', 'run', '--profile', CALDERA_PROFILE_PATH],
    'openvas': ['gvm-cli', 'socket', '--xml', OPENVAS_XML],
}


def _run_tool(job_id, command):
    """Execute a security tool and capture its output.

    Results are stored in-memory for quick access and additionally written to
    ``/var/log/trainee`` for later inspection.  The file extension is chosen
    based on the tool invoked to better reflect the typical output format.
    """

    jobs[job_id]['status'] = 'running'
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
    except FileNotFoundError as exc:  # tool missing
        jobs[job_id]['status'] = 'failed'
        jobs[job_id]['output'] = str(exc)
        return
    except subprocess.CalledProcessError as exc:  # execution error
        jobs[job_id]['status'] = 'failed'
        jobs[job_id]['output'] = exc.stderr
        return

    jobs[job_id]['status'] = 'completed'
    jobs[job_id]['output'] = result.stdout

    # Persist full output to disk for instructor review
    log_dir = '/var/log/trainee'
    os.makedirs(log_dir, exist_ok=True)
    tool = jobs[job_id]['tool']
    ext = 'html' if tool in {'zap', 'openvas'} else 'txt'
    file_path = os.path.join(log_dir, f'{tool}_{job_id}.{ext}')
    try:
        with open(file_path, 'w', encoding='utf-8') as fh:
            fh.write(result.stdout)
        jobs[job_id]['output_file'] = file_path
    except OSError:
        # Failure to persist the file should not mark the job as failed
        pass


def _validate_tool(command):
    """Return (bool, error_message) based on tool availability."""

    tool_name = command[0]
    if shutil.which(tool_name):
        return True, ''
    return False, f"Required tool '{tool_name}' is not installed or not in PATH."


def authenticate(token):
    if not token:
        return None

    session = get_session_by_token(token)
    if not session:
        app.logger.warning('AUDIT auth_failed reason=missing_session token=%s', token)
        return None

    now = time.time()
    if session.get('revoked_at') is not None:
        app.logger.warning(
            'AUDIT auth_failed reason=revoked token=%s username=%s revoked_at=%s',
            token,
            session.get('username'),
            session.get('revoked_at'),
        )
        return None

    if session.get('expires_at') is not None and now >= session['expires_at']:
        revoke_session(token, revoked_at=now)
        app.logger.warning(
            'AUDIT auth_failed reason=expired token=%s username=%s expired_at=%s',
            token,
            session.get('username'),
            session.get('expires_at'),
        )
        return None

    return get_user(session['username'])


def token_username(token):
    session = get_session_by_token(token)
    return session['username'] if session else None


def _extract_token():
    if request.method == 'GET':
        return request.args.get('token')
    data = request.get_json(silent=True) or {}
    return data.get('token')


def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = _extract_token()
        user = authenticate(token)
        if not user:
            return jsonify({'error': 'unauthorized'}), 403
        g.current_user = user
        g.auth_token = token
        return fn(*args, **kwargs)

    return wrapper


def require_role(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = getattr(g, 'current_user', None)
            if not user or user.get('role') not in roles:
                return jsonify({'error': 'unauthorized'}), 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def _is_elevated(user):
    return user.get('role') in {'instructor', 'admin'}


def _resolve_username(payload, user):
    requested_username = payload.get('username')
    authenticated_username = user['username']
    if requested_username and requested_username != authenticated_username and not _is_elevated(user):
        return None, 'username override not allowed'
    return requested_username or authenticated_username, None


def _validate_course_ownership(course_id, user, *, instructor_owned=False):
    if not course_id:
        return False, 'course_id required', 400
    course = courses.get(course_id)
    if not course:
        return False, 'course not found', 404
    if user.get('role') == 'admin':
        return True, None, None
    if instructor_owned and (
        user.get('role') != 'instructor' or course.get('instructor') != user['username']
    ):
        return False, 'forbidden course ownership', 403
    return True, None, None


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json(force=True)
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'trainee')
    if not username or not password:
        return jsonify({'error': 'username and password required'}), 400
    if get_user(username):
        return jsonify({'error': 'user exists'}), 400
    try:
        password_hash = hash_password(password)
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400
    create_user(username, password_hash, role)
    return jsonify({'status': 'registered'})


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(force=True)
    username = data.get('username')
    password = data.get('password')
    user = get_user(username)
    if not user or not verify_password(password, user['password']):
        return jsonify({'error': 'invalid credentials'}), 403
    token = str(uuid.uuid4())
    issued_at = time.time()
    expires_at = issued_at + SESSION_TTL_SECONDS
    create_session(token, username, issued_at, expires_at)
    return jsonify({'token': token})


@app.route('/logout', methods=['POST'])
def logout():
    data = request.get_json(force=True)
    token = data.get('token')
    if not token:
        return jsonify({'error': 'token required'}), 400

    user = authenticate(token)
    if not user:
        return jsonify({'error': 'unauthorized'}), 403

    revoke_session(token, revoked_at=time.time())
    app.logger.info('AUDIT logout_success token=%s username=%s', token, user['username'])
    return jsonify({'status': 'logged_out'})


@app.route('/courses', methods=['POST'])
@require_auth
@require_role('instructor', 'admin')
def create_course():
    data = request.get_json(force=True)
    user = g.current_user
    title = data.get('title')
    content = data.get('content', '')
    course_id = str(uuid.uuid4())
    courses[course_id] = {
        'title': title,
        'content': content,
        'instructor': user['username']
    }
    return jsonify({'course_id': course_id})


@app.route('/courses', methods=['GET'])
def list_courses():
    token = request.args.get('token')
    user = authenticate(token)
    if not user:
        return jsonify({'error': 'unauthorized'}), 403
    return jsonify(courses)


@app.route('/invites', methods=['POST'])
@require_auth
@require_role('instructor', 'admin')
def create_invite():
    data = request.get_json(force=True)
    user = g.current_user
    course_id = data.get('course_id')
    email = data.get('email')
    ok, message, status = _validate_course_ownership(course_id, user, instructor_owned=True)
    if not ok:
        return jsonify({'error': message}), status
    code = str(uuid.uuid4())
    invites[code] = {'course_id': course_id, 'email': email}
    return jsonify({'invite_code': code})


@app.route('/progress', methods=['POST'])
def update_progress():
    data = request.get_json(force=True)
    token = data.get('token')
    user = authenticate(token)
    if not user:
        return jsonify({'error': 'unauthorized'}), 403
    course_id = data.get('course_id')
    username = data.get('username') or token_username(token)
    value = data.get('progress')
    progress[(course_id, username)] = value
    return jsonify({'status': 'updated'})


@app.route('/progress', methods=['GET'])
def get_progress():
    token = request.args.get('token')
    user = authenticate(token)
    if not user:
        return jsonify({'error': 'unauthorized'}), 403
    course_id = request.args.get('course_id')
    username = request.args.get('username') or token_username(token)
    value = progress.get((course_id, username), 0)
    return jsonify({'progress': value})


@app.route('/results', methods=['POST'])
@require_auth
def post_results():
    data = request.get_json(force=True)
    user = g.current_user
    course_id = data.get('course_id')
    ok, message, status = _validate_course_ownership(course_id, user)
    if not ok:
        return jsonify({'error': message}), status
    if _is_elevated(user):
        ok, message, status = _validate_course_ownership(course_id, user, instructor_owned=True)
        if not ok:
            return jsonify({'error': message}), status
    username, username_error = _resolve_username(data, user)
    if username_error:
        return jsonify({'error': username_error}), 403
    start = data.get('start_time')
    end = data.get('end_time')
    score = data.get('score', 0)
    duration = None
    if start is not None and end is not None:
        try:
            duration = float(end) - float(start)
        except (TypeError, ValueError):
            duration = None
    result = {
        'course_id': course_id,
        'username': username,
        'score': score,
        'duration': duration,
        'details': data.get('details', {}),
        'timestamp': time.time(),
    }
    append_result(result)
    metrics = aggregate_results(course_id, username)
    quiz = quiz_results.get((course_id, username))
    if quiz:
        metrics['quiz_score'] = quiz.get('score', 0)
    progress[(course_id, username)] = metrics.get('score', score)
    ok_progress, message_progress = open_edx.update_progress(username, course_id, metrics)
    ok_grade, message_grade = open_edx.push_grade_lms(
        username, course_id, metrics.get('score', score)
    )
    if not ok_progress:
        edx_failures.append(
            {
                'course_id': course_id,
                'username': username,
                'error': message_progress,
                'timestamp': time.time(),
            }
        )
    if not ok_grade:
        edx_failures.append(
            {
                'course_id': course_id,
                'username': username,
                'error': message_grade,
                'timestamp': time.time(),
            }
        )
    return jsonify(
        {
            'status': 'recorded',
            'metrics': metrics,
            'edx_sync': ok_progress and ok_grade,
        }
    )


@app.route('/edx_failures', methods=['GET'])
@require_auth
@require_role('instructor', 'admin')
def get_edx_failures():
    user = g.current_user
    if user['role'] == 'admin':
        return jsonify({'failures': edx_failures})
    visible = [
        failure
        for failure in edx_failures
        if courses.get(failure.get('course_id'), {}).get('instructor') == user['username']
    ]
    return jsonify({'failures': visible})


@app.route('/launch_tool', methods=['POST'])
@require_auth
def launch_tool():
    data = request.get_json(force=True)
    user = g.current_user
    course_id = data.get('course_id')
    if course_id:
        ok, message, status = _validate_course_ownership(course_id, user)
        if not ok:
            return jsonify({'error': message}), status
        if _is_elevated(user):
            ok, message, status = _validate_course_ownership(course_id, user, instructor_owned=True)
            if not ok:
                return jsonify({'error': message}), status
    _, username_error = _resolve_username(data, user)
    if username_error:
        return jsonify({'error': username_error}), 403

    tool = data.get('tool', '').lower()
    command = COMMANDS.get(tool)
    if not command:
        return jsonify({'error': 'invalid tool'}), 400

    ok, message = _validate_tool(command)
    if not ok:
        return jsonify({'error': message}), 500

    job_id = str(uuid.uuid4())
    jobs[job_id] = {'status': 'pending', 'tool': tool}
    thread = threading.Thread(target=_run_tool, args=(job_id, command), daemon=True)
    thread.start()

    return jsonify({'job_id': job_id, 'status': jobs[job_id]['status']})


@app.route('/launch_tool/<job_id>', methods=['GET'])
def launch_tool_status(job_id):
    token = request.args.get('token')
    user = authenticate(token)
    if not user:
        return jsonify({'error': 'unauthorized'}), 403

    job = jobs.get(job_id)
    if not job:
        return jsonify({'error': 'not found'}), 404

    return jsonify(job)


@app.route('/kypo/launch', methods=['POST'])
@require_auth
def kypo_launch():
    """Generate an LTI launch URL for a KYPO lab.

    The endpoint expects a JSON body with a valid authentication token
    and ``lab_id`` identifying the KYPO exercise. The response contains
    a pre-signed LTI launch URL that the caller can redirect the user to
    in order to start the session.
    """

    data = request.get_json(force=True)
    token = g.auth_token
    lab_id = data.get('lab_id')
    user = g.current_user
    course_id = data.get('course_id')
    if course_id:
        ok, message, status = _validate_course_ownership(course_id, user)
        if not ok:
            return jsonify({'error': message}), status
        if _is_elevated(user):
            ok, message, status = _validate_course_ownership(course_id, user, instructor_owned=True)
            if not ok:
                return jsonify({'error': message}), status
    _, username_error = _resolve_username(data, user)
    if username_error:
        return jsonify({'error': username_error}), 403

    if not lab_id:
        return jsonify({'error': 'lab_id required'}), 400

    username = token_username(token)
    try:
        launch_url = open_edx.generate_launch_url(username, lab_id)
    except Exception as exc:  # pragma: no cover - configuration errors
        return jsonify({'error': str(exc)}), 500

    return jsonify({'launch_url': launch_url})


init_schema()
app.logger.info('Training DB path: %s', TRAINING_DB_PATH)

phishing_quiz.init_app(app, authenticate, token_username, quiz_results, open_edx, edx_failures)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
