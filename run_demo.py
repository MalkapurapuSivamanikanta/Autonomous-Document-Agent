"""Run BOTH required test inputs end to end and save the evidence.

    python run_demo.py

For each sample in samples/ it calls POST /agent (in-process, no server needed), prints the
agent-generated plan, and saves the JSON response and the Word file into demo_results/.
Great to have open during the video recording.
"""

import json
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from main import app

ROOT = Path(__file__).resolve().parent
SAMPLES = ["standard", "complex"]
RESULTS_DIR = ROOT / "demo_results"


def run_sample(client: TestClient, name: str, results_dir: Path) -> bool:
    payload = json.loads((ROOT / "samples" / f"{name}.json").read_text())
    print(f"\n{'=' * 78}\n{name.upper()} REQUEST\n{payload['request']}\n{'=' * 78}")

    response = client.post("/agent", json=payload)
    if response.status_code != 200:
        print(f"FAILED: HTTP {response.status_code}: {response.json().get('detail')}")
        return False

    body = response.json()
    print(f"\n{body['message']}")
    print(f"\nPlanning rationale:\n  {body['plan_reasoning']}")
    print("\nAssumptions:")
    for assumption in body["assumptions"]:
        print(f"  - {assumption}")
    print("\nAgent-generated task list:")
    for task in body["task_list"]:
        print(f"  {task['id']}. {task['section']}: {task['goal']}")

    results_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / f"{name}_response.json").write_text(json.dumps(body, indent=2))
    download = client.get(body["download_url"])
    (results_dir / f"{name}.docx").write_bytes(download.content)
    print(f"\nSaved: {results_dir / (name + '.docx')}")
    return download.status_code == 200


def main(results_dir: Path = RESULTS_DIR) -> int:
    client = TestClient(app)
    results = [run_sample(client, name, results_dir) for name in SAMPLES]
    print(f"\n{'=' * 78}\n{sum(results)}/{len(results)} test inputs succeeded")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
