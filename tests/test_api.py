from fastapi.testclient import TestClient

from main import app
from tests.conftest import failing

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_too_short_request_is_422():
    assert client.post("/agent", json={"request": "hi"}).status_code == 422


def test_blank_request_is_422():
    assert client.post("/agent", json={"request": "              "}).status_code == 422


def test_missing_field_is_422():
    assert client.post("/agent", json={}).status_code == 422


def test_agent_endpoint_returns_plan_assumptions_and_download_link(fake_llm):
    response = client.post("/agent", json={"request": "Create a project plan for launching an app."})
    assert response.status_code == 200
    body = response.json()
    assert len(body["task_list"]) == 7
    assert body["assumptions"] == ["Assumed budget"]
    assert body["plan_reasoning"]

    download = client.get(body["download_url"])
    assert download.status_code == 200
    assert download.headers["content-type"].startswith("application/vnd.openxmlformats")


def test_llm_failure_maps_to_502(fake_llm):
    fake_llm.behavior = failing("down")
    response = client.post("/agent", json={"request": "Create a project plan for launching an app."})
    assert response.status_code == 502


def test_unexpected_error_maps_to_500(monkeypatch):
    def boom(_):
        raise ValueError("unexpected")

    monkeypatch.setattr("services.agent_service.generate_document", boom)
    response = client.post("/agent", json={"request": "Create a project plan for launching an app."})
    assert response.status_code == 500


def test_download_blocks_bad_names_and_traversal(tmp_path):
    (tmp_path.parent / "secret.docx").write_text("secret")  # a file OUTSIDE the output folder
    assert client.get("/download/notes.txt").status_code == 404
    assert client.get("/download/missing.docx").status_code == 404
    assert client.get("/download/..%2Fsecret.docx").status_code == 404
    assert client.get("/download/../secret.docx").status_code == 404
