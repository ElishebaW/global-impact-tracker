"""Generate a live impact dashboard HTML page from tracker logs."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

from tracker import GlobalImpactTracker


HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Live Impact Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {
      --bg: #f5f7fb;
      --panel: #ffffff;
      --ink: #1d2433;
      --accent: #0a84ff;
      --accent-2: #17b26a;
      --muted: #5f6b85;
      --line: #dbe2f0;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      font-family: "Avenir Next", "Segoe UI", sans-serif;
      color: var(--ink);
      background: radial-gradient(circle at top right, #e7f0ff 0%, var(--bg) 45%);
      min-height: 100vh;
      padding: 24px;
    }

    .container {
      max-width: 1040px;
      margin: 0 auto;
      display: grid;
      gap: 20px;
    }

    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 20px;
      box-shadow: 0 8px 30px rgba(18, 34, 66, 0.07);
    }

    .kicker {
      letter-spacing: 0.08em;
      font-weight: 700;
      color: var(--muted);
      font-size: 0.78rem;
      text-transform: uppercase;
      margin: 0 0 6px;
    }

    .ticker {
      font-size: clamp(2rem, 4vw, 3rem);
      font-weight: 800;
      color: var(--accent-2);
      margin: 0;
    }

    h1 {
      margin: 0;
      font-size: clamp(1.4rem, 2vw, 2rem);
    }

    p {
      margin: 10px 0 0;
      color: var(--muted);
      line-height: 1.55;
    }

    #chartWrap {
      height: min(58vh, 420px);
    }

    canvas { max-height: 100%; }
  </style>
</head>
<body>
  <main class="container">
    <section class="panel">
      <p class="kicker">Total Hours Saved</p>
      <p class="ticker" id="hoursSavedTicker">0.00 hours</p>
      <p>Calculated as projected manual hours minus actual AI-orchestrated execution hours.</p>
    </section>

    <section class="panel">
      <h1>Projected Manual vs Actual AI-Orchestrated Hours</h1>
      <p>Bar chart by project based on logged execution history.</p>
      <div id="chartWrap">
        <canvas id="impactChart" aria-label="Impact comparison chart"></canvas>
      </div>
    </section>

    <section class="panel">
      <h1>Why</h1>
      <p>
        I built this tool to quantify the transition from manual execution to AI orchestration.
        It serves as a real-time audit of my efficiency, proving a 90%+ reduction in task latency across multiple live projects.
      </p>
    </section>
  </main>

  <script>
    const labels = __LABELS__;
    const projectedHours = __PROJECTED_HOURS__;
    const actualHours = __ACTUAL_HOURS__;
    const totalSavedHours = __TOTAL_SAVED_HOURS__;

    const ticker = document.getElementById("hoursSavedTicker");
    const durationMs = 1600;
    const startTime = performance.now();

    function updateTicker(now) {
      const t = Math.min((now - startTime) / durationMs, 1);
      const eased = 1 - Math.pow(1 - t, 3);
      const value = totalSavedHours * eased;
      ticker.textContent = `${value.toFixed(2)} hours`;
      if (t < 1) requestAnimationFrame(updateTicker);
    }

    requestAnimationFrame(updateTicker);

    new Chart(document.getElementById("impactChart"), {
      type: "bar",
      data: {
        labels,
        datasets: [
          {
            label: "Projected Manual Hours",
            data: projectedHours,
            backgroundColor: "rgba(10, 132, 255, 0.75)",
            borderColor: "rgba(10, 132, 255, 1)",
            borderWidth: 1,
            borderRadius: 8
          },
          {
            label: "Actual AI-Orchestrated Hours",
            data: actualHours,
            backgroundColor: "rgba(23, 178, 106, 0.75)",
            borderColor: "rgba(23, 178, 106, 1)",
            borderWidth: 1,
            borderRadius: 8
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: (value) => `${value}h`
            },
            title: {
              display: true,
              text: "Hours"
            }
          }
        }
      }
    });
  </script>
</body>
</html>
"""


def _collect_dashboard_data(log_file: Path) -> tuple[list[str], list[float], list[float], float]:
    project_manual = defaultdict(float)
    project_ai = defaultdict(float)

    if log_file.exists():
        with open(log_file, "r", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                project = row.get("Project", "Unknown") or "Unknown"
                baseline_hrs = float(row.get("Human_Baseline_Hrs", 0) or 0)
                ai_seconds = float(row.get("AI_Sec", 0) or 0)

                project_manual[project] += baseline_hrs
                project_ai[project] += ai_seconds / 3600.0

    labels = sorted(project_manual.keys())
    projected = [round(project_manual[name], 4) for name in labels]
    actual = [round(project_ai[name], 4) for name in labels]

    total_projected = sum(projected)
    total_actual = sum(actual)
    total_saved = round(max(total_projected - total_actual, 0.0), 4)

    return labels, projected, actual, total_saved


def generate_dashboard(output_file: Path) -> Path:
    tracker = GlobalImpactTracker()
    labels, projected, actual, total_saved = _collect_dashboard_data(tracker.log_file)

    html = (
        HTML_TEMPLATE.replace("__LABELS__", json.dumps(labels))
        .replace("__PROJECTED_HOURS__", json.dumps(projected))
        .replace("__ACTUAL_HOURS__", json.dumps(actual))
        .replace("__TOTAL_SAVED_HOURS__", json.dumps(total_saved))
    )

    output_file.write_text(html, encoding="utf-8")
    return output_file


def main() -> None:
    output_path = Path(__file__).resolve().parent / "live_impact_dashboard.html"
    generated = generate_dashboard(output_path)
    print(f"Live dashboard generated at: {generated}")


if __name__ == "__main__":
    main()
