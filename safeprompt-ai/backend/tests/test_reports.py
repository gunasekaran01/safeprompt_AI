"""
Tests for the Milestone 13 PDF report route (app/api/routes/reports.py),
backed by app/services/report_service.py (reportlab) and the fake
Supabase `reports` table (tests/conftest.py's autouse `fake_supabase`
fixture).

Writes real PDF files to a temporary REPORTS_DIR for the duration of the
test session so the real `backend/reports/` directory is never touched by
the test suite.
"""

import os

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from tests.conftest import AUTH_HEADERS, TEST_USER_ID

client = TestClient(app, headers=AUTH_HEADERS)


def test_get_report_generates_and_downloads_a_pdf(tmp_path, monkeypatch):
    monkeypatch.setattr(get_settings(), "REPORTS_DIR", str(tmp_path))

    created = client.post("/api/analyze", json={"prompt": "Hello, how can I help you today?"})
    analysis_id = created.json()["id"]

    response = client.get(f"/api/reports/{analysis_id}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content[:4] == b"%PDF"


def test_get_report_records_metadata_in_supabase(tmp_path, monkeypatch):
    """
    Verifies persistence through app/services/history_service.py's
    create_report_record (the live path -- see app/api/reports.py), not
    the old app/db/crud.py:create_report/list_reports_for_analysis, which
    is unwired from any route and writes/reads through a completely
    separate fake client than the one the live route actually uses.
    Checking via crud here previously always found zero records
    regardless of whether the real route worked, and asserted on a
    'format' field the current `reports` table schema doesn't have.
    """
    monkeypatch.setattr(get_settings(), "REPORTS_DIR", str(tmp_path))

    created = client.post("/api/analyze", json={"prompt": "Another prompt for reporting."})
    analysis_id = created.json()["id"]

    client.get(f"/api/reports/{analysis_id}")

    from app.db.supabase_client import get_supabase_client

    response = (
        get_supabase_client().table("reports").select("*").eq("analysis_id", analysis_id).execute()
    )
    records = response.data
    assert len(records) == 1
    assert records[0]["analysis_id"] == analysis_id
    assert records[0]["user_id"] == TEST_USER_ID
    assert records[0]["file_path"]


def test_get_report_returns_404_for_unknown_analysis():
    response = client.get("/api/reports/does-not-exist")
    assert response.status_code == 404
