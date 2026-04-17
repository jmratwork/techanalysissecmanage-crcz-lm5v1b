"""Result handling utilities and listener service.

This module stores raw result entries in SQLite and exposes an optional Flask
application that can be used as a lightweight listener service.
"""

from __future__ import annotations

from typing import Any, Dict

from flask import Flask, jsonify, request

from storage import aggregate_result_metrics, append_result_record


def append_result(result: Dict[str, Any]) -> None:
    """Append a result entry to persistent storage."""
    append_result_record(result)


def aggregate_results(course_id: str, username: str) -> Dict[str, Any]:
    """Return aggregated metrics for the given course and user.

    The current aggregation sums ``score`` values and returns a list of unique
    ``flag`` identifiers that were submitted by the trainee.  The structure is
    intentionally simple so it can be easily extended in the future.
    """

    return aggregate_result_metrics(course_id, username)


# ---------------------------------------------------------------------------
# Listener service
app = Flask(__name__)


@app.post("/listener")
def listener() -> Any:
    """Endpoint receiving score/flag data from the KYPO range.

    Expected JSON payload::

        {
            "username": "trainee1",
            "course_id": "course-uuid",
            "score": 10,
            "flag": "flag-1"
        }

    The result is stored in SQLite and aggregated metrics are returned in the
    response.
    """

    data = request.get_json(force=True)
    result = {
        "username": data.get("username"),
        "course_id": data.get("course_id"),
        "score": data.get("score", 0),
        "flag": data.get("flag"),
        "details": data.get("details", {}),
    }
    append_result(result)
    metrics = aggregate_results(result["course_id"], result["username"])
    return jsonify({"status": "recorded", "metrics": metrics})


if __name__ == "__main__":  # pragma: no cover - manual service start
    app.run(host="0.0.0.0", port=6000)
