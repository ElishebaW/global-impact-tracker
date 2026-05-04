from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from conftest import src_env


def test_python_module_entrypoint_prints_metrics_snapshot(tmp_path):
    result = subprocess.run(
        [sys.executable, "-m", "global_impact_tracker", "metrics"],
        cwd=Path(__file__).parent.parent,
        env=src_env(home=tmp_path),
        check=True,
        capture_output=True,
        text=True,
    )

    assert '"queries_processed"' in result.stdout
    assert "Snapshot saved to:" in result.stdout
