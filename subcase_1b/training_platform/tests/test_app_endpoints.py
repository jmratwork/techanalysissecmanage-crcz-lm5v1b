import importlib
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from types import ModuleType
from unittest.mock import Mock

import pytest


@pytest.fixture()
def app_module(monkeypatch, tmp_path):
    """Load training app with an isolated SQLite DB and fresh module state."""

    root = Path(__file__).resolve().parents[1]
    monkeypatch.setenv("TRAINING_DB_PATH", str(tmp_path / "training_platform.sqlite3"))
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    for module_name in ["app", "storage", "results_service", "phishing_quiz", "open_edx_client"]:
        sys.modules.pop(module_name, None)

    fake_security = ModuleType("security")
    fake_security.hash_password = lambda password: f"hashed::{password}"
    fake_security.verify_password = lambda password, stored: stored == f"hashed::{password}"
    sys.modules["security"] = fake_security

    module = importlib.import_module("app")

    module.courses.clear()
    module.invites.clear()
    return module


@pytest.fixture()
def client(app_module):
    app_module.app.config.update(TESTING=True)
    return app_module.app.test_client()


def _register_and_login(client, username, password="secret123", role="trainee"):
    register_response = client.post(
        "/register",
        json={"username": username, "password": password, "role": role},
    )
    assert register_response.status_code == 200

    login_response = client.post(
        "/login",
        json={"username": username, "password": password},
    )
    assert login_response.status_code == 200
    return login_response.get_json()["token"]


def _create_course(client, instructor_token, title="Intro"):
    response = client.post(
        "/courses",
        json={"token": instructor_token, "title": title, "content": "content"},
    )
    assert response.status_code == 200
    return response.get_json()["course_id"]


def test_register_login_logout_flow(client):
    register_ok = client.post(
        "/register",
        json={"username": "alice", "password": "pass123", "role": "trainee"},
    )
    assert register_ok.status_code == 200

    duplicate = client.post(
        "/register",
        json={"username": "alice", "password": "pass123"},
    )
    assert duplicate.status_code == 400

    bad_login = client.post("/login", json={"username": "alice", "password": "bad"})
    assert bad_login.status_code == 403

    login_ok = client.post("/login", json={"username": "alice", "password": "pass123"})
    assert login_ok.status_code == 200
    token = login_ok.get_json()["token"]

    logout_ok = client.post("/logout", json={"token": token})
    assert logout_ok.status_code == 200

    after_logout = client.get("/courses", query_string={"token": token})
    assert after_logout.status_code == 403


def test_courses_requires_auth_and_role(client):
    trainee_token = _register_and_login(client, "trainee1", role="trainee")

    unauthorized = client.post("/courses", json={"title": "T1"})
    assert unauthorized.status_code == 403

    forbidden = client.post(
        "/courses",
        json={"token": trainee_token, "title": "T1", "content": "x"},
    )
    assert forbidden.status_code == 403

    instructor_token = _register_and_login(client, "instr1", role="instructor")
    course_id = _create_course(client, instructor_token, title="Course A")
    assert course_id

    listed = client.get("/courses", query_string={"token": instructor_token})
    assert listed.status_code == 200
    assert course_id in listed.get_json()


def test_quiz_start_submit_score(client, app_module):
    push_grade = Mock(return_value=(True, ""))
    push_grade_lms = Mock(return_value=(True, ""))
    app_module.open_edx.push_grade = push_grade
    app_module.open_edx.push_grade_lms = push_grade_lms

    token = _register_and_login(client, "quizuser", role="trainee")
    instructor = _register_and_login(client, "quizinst", role="instructor")
    course_id = _create_course(client, instructor)

    unauthorized = client.get("/quiz/start")
    assert unauthorized.status_code == 403

    start = client.get("/quiz/start", query_string={"token": token, "course_id": course_id})
    assert start.status_code == 200
    questions = start.get_json()["questions"]
    assert len(questions) >= 1
    assert all("answer" not in q for q in questions)

    answers = {"q1": 2, "q2": 1, "q3": 0}
    submit = client.post(
        "/quiz/submit",
        json={"token": token, "course_id": course_id, "answers": answers},
    )
    assert submit.status_code == 200
    assert submit.get_json()["score"] >= 3

    score = client.get("/quiz/score", query_string={"token": token, "course_id": course_id})
    assert score.status_code == 200
    assert score.get_json()["score"] >= 3

    assert push_grade.called
    assert push_grade_lms.called


def test_results_success_and_edx_failure_record(client, app_module):
    token = _register_and_login(client, "learner", role="trainee")
    instructor = _register_and_login(client, "inst2", role="instructor")
    course_id = _create_course(client, instructor)

    app_module.open_edx.update_progress = Mock(return_value=(True, ""))
    app_module.open_edx.push_grade_lms = Mock(return_value=(True, ""))

    success = client.post(
        "/results",
        json={
            "token": token,
            "course_id": course_id,
            "score": 7,
            "start_time": 1,
            "end_time": 5,
            "details": {"phase": "lab"},
        },
    )
    assert success.status_code == 200
    body = success.get_json()
    assert body["status"] == "recorded"
    assert body["edx_sync"] is True

    app_module.open_edx.update_progress = Mock(return_value=(False, "progress failed"))
    app_module.open_edx.push_grade_lms = Mock(return_value=(False, "grade failed"))

    failed_sync = client.post(
        "/results",
        json={"token": token, "course_id": course_id, "score": 2},
    )
    assert failed_sync.status_code == 200
    assert failed_sync.get_json()["edx_sync"] is False

    failures = client.get("/edx_failures", query_string={"token": instructor})
    assert failures.status_code == 200
    errors = [entry["error"] for entry in failures.get_json()["failures"]]
    assert "progress failed" in errors
    assert "grade failed" in errors


def test_launch_tool_and_status_with_subprocess_mock(client, app_module, monkeypatch):
    token = _register_and_login(client, "operator", role="trainee")

    fake_result = SimpleNamespace(stdout="scan ok")
    run_mock = Mock(return_value=fake_result)
    monkeypatch.setattr(app_module.subprocess, "run", run_mock)
    monkeypatch.setattr(app_module, "_validate_tool", lambda command: (True, ""))

    class ImmediateThread:
        def __init__(self, target, args, daemon):
            self.target = target
            self.args = args

        def start(self):
            self.target(*self.args)

    monkeypatch.setattr(app_module.threading, "Thread", ImmediateThread)

    launch = client.post(
        "/launch_tool",
        json={"token": token, "tool": "nmap"},
    )
    assert launch.status_code == 200
    job_id = launch.get_json()["job_id"]
    assert run_mock.called

    status = client.get(f"/launch_tool/{job_id}", query_string={"token": token})
    assert status.status_code == 200
    payload = status.get_json()
    assert payload["status"] == "completed"
    assert payload["output"] == "scan ok"

    monkeypatch.setattr(
        app_module.subprocess,
        "run",
        Mock(side_effect=subprocess.CalledProcessError(returncode=1, cmd=["nmap"], stderr="boom")),
    )

    second = client.post("/launch_tool", json={"token": token, "tool": "nmap"})
    second_id = second.get_json()["job_id"]
    failed_job = client.get(f"/launch_tool/{second_id}", query_string={"token": token})
    assert failed_job.status_code == 200
    assert failed_job.get_json()["status"] == "failed"

    unknown_job = client.get("/launch_tool/missing", query_string={"token": token})
    assert unknown_job.status_code == 404


def test_kypo_launch_success_and_error(client, app_module):
    token = _register_and_login(client, "kypo-user", role="trainee")

    missing = client.post("/kypo/launch", json={"token": token})
    assert missing.status_code == 400

    app_module.open_edx.generate_launch_url = Mock(return_value="https://kypo.example/launch")
    ok = client.post("/kypo/launch", json={"token": token, "lab_id": "lab-1"})
    assert ok.status_code == 200
    assert ok.get_json()["launch_url"].startswith("https://kypo.example")

    app_module.open_edx.generate_launch_url = Mock(side_effect=RuntimeError("kypo down"))
    failed = client.post("/kypo/launch", json={"token": token, "lab_id": "lab-1"})
    assert failed.status_code == 500
    assert failed.get_json()["error"] == "kypo down"
