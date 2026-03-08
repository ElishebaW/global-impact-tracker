"""Generate a live impact dashboard HTML page from tracker logs."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

from tracker import GlobalImpactTracker


HTML_TEMPLATE = """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>Live Impact Dashboard</title>
  <script src=\"https://cdn.jsdelivr.net/npm/chart.js\"></script>
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
      font-family: \"Avenir Next\", \"Segoe UI\", sans-serif;
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

    .star-grid {
      margin-top: 14px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
    }

    .star-card {
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 12px;
      background: #f9fbff;
    }

    .star-label {
      margin: 0;
      font-size: 0.78rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--muted);
      font-weight: 700;
    }

    .star-value {
      margin: 6px 0 0;
      font-size: 1.5rem;
      font-weight: 800;
      color: var(--ink);
    }

    .star-copy {
      margin-top: 14px;
      padding-left: 20px;
      color: var(--muted);
      line-height: 1.5;
    }

    #chartWrap {
      height: min(58vh, 420px);
    }

    canvas { max-height: 100%; }
  </style>
</head>
<body>
  <main class=\"container\">
    <section class=\"panel\">
      <p class=\"kicker\">Total Hours Saved</p>
      <p class=\"ticker\" id=\"hoursSavedTicker\">0.00 hours</p>
      <p>Calculated as projected manual hours minus actual AI-orchestrated execution hours.</p>
    </section>

    <section class=\"panel\">
      <h1>Projected Manual vs Actual AI-Orchestrated Hours</h1>
      <p>Bar chart by project based on logged execution history.</p>
      <div id=\"chartWrap\">
        <canvas id=\"impactChart\" aria-label=\"Impact comparison chart\"></canvas>
      </div>
    </section>

    <section class=\"panel\">
      <h1>STAR Story Metrics</h1>
      <p>Live metrics mapped to Situation, Task, Action, and Result.</p>
      <div class=\"star-grid\">
        <article class=\"star-card\">
          <p class=\"star-label\">Situation</p>
          <p class=\"star-value\" id=\"projectsCount\">0</p>
          <p>Active projects with logged orchestration impact.</p>
        </article>
        <article class=\"star-card\">
          <p class=\"star-label\">Task</p>
          <p class=\"star-value\" id=\"projectedTotal\">0.00h</p>
          <p>Projected manual hours before automation.</p>
        </article>
        <article class=\"star-card\">
          <p class=\"star-label\">Action</p>
          <p class=\"star-value\" id=\"aiActualTotal\">0.00h</p>
          <p>Actual AI-orchestrated execution hours.</p>
        </article>
        <article class=\"star-card\">
          <p class=\"star-label\">Result</p>
          <p class=\"star-value\" id=\"latencyReduction\">0.00%</p>
          <p>Reduction in latency from manual baseline.</p>
        </article>
      </div>
      <ol class=\"star-copy\">
        <li><strong>Situation:</strong> __SITUATION_TEXT__</li>
        <li><strong>Task:</strong> __TASK_TEXT__</li>
        <li><strong>Action:</strong> __ACTION_TEXT__</li>
        <li><strong>Result:</strong> __RESULT_TEXT__</li>
      </ol>
    </section>

    <section class=\"panel\">
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
    const starMetrics = __STAR_METRICS__;

    const ticker = document.getElementById(\"hoursSavedTicker\");
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

    document.getElementById(\"projectsCount\").textContent = starMetrics.projects_count;
    document.getElementById(\"projectedTotal\").textContent = `${starMetrics.projected_total.toFixed(2)}h`;
    document.getElementById(\"aiActualTotal\").textContent = `${starMetrics.actual_total.toFixed(2)}h`;
    document.getElementById(\"latencyReduction\").textContent = `${starMetrics.reduction_pct.toFixed(2)}%`;

    new Chart(document.getElementById(\"impactChart\"), {
      type: \"bar\",
      data: {
        labels,
        datasets: [
          {
            label: \"Projected Manual Hours\",
            data: projectedHours,
            backgroundColor: \"rgba(10, 132, 255, 0.75)\",
            borderColor: \"rgba(10, 132, 255, 1)\",
            borderWidth: 1,
            borderRadius: 8
          },
          {
            label: \"Actual AI-Orchestrated Hours\",
            data: actualHours,
            backgroundColor: \"rgba(23, 178, 106, 0.75)\",
            borderColor: \"rgba(23, 178, 106, 1)\",
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
              text: \"Hours\"
            }
          }
        }
      }
    });
  </script>
</body>
</html>
"""


def _to_float(value: str | None) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _collect_dashboard_data(log_file: Path) -> tuple[list[str], list[float], list[float], float, dict[str, float | int | str]]:
    project_manual = defaultdict(float)
    project_ai = defaultdict(float)
    rows = []

    if log_file.exists():
        with open(log_file, "r", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                project = row.get("Project", "Unknown") or "Unknown"
                baseline_hrs = _to_float(row.get("Human_Baseline_Hrs"))
                ai_seconds = _to_float(row.get("AI_Sec"))

                project_manual[project] += baseline_hrs
                project_ai[project] += ai_seconds / 3600.0
                rows.append(row)

    labels = sorted(project_manual.keys())
    projected = [round(project_manual[name], 4) for name in labels]
    actual = [round(project_ai[name], 4) for name in labels]

    total_projected = round(sum(projected), 4)
    total_actual = round(sum(actual), 4)
    total_saved = round(max(total_projected - total_actual, 0.0), 4)
    reduction_pct = round((total_saved / total_projected) * 100, 2) if total_projected > 0 else 0.0

    projects_count = len(labels)
    tasks_count = len(rows)
    situation_text = f"{projects_count} live projects and {tasks_count} tracked tasks required a measurable efficiency baseline."
    task_text = f"Manual execution was projected at {total_projected:.2f} total hours."
    action_text = f"AI orchestration completed the same work in {total_actual:.2f} actual hours."
    result_text = f"Net savings: {total_saved:.2f} hours with a {reduction_pct:.2f}% latency reduction."

    star_metrics = {
        "projects_count": projects_count,
        "tasks_count": tasks_count,
        "projected_total": total_projected,
        "actual_total": total_actual,
        "saved_total": total_saved,
        "reduction_pct": reduction_pct,
        "situation_text": situation_text,
        "task_text": task_text,
        "action_text": action_text,
        "result_text": result_text,
    }

    return labels, projected, actual, total_saved, star_metrics


def generate_dashboard(output_file: Path) -> Path:
    tracker = GlobalImpactTracker()
    labels, projected, actual, total_saved, star_metrics = _collect_dashboard_data(tracker.log_file)

    html = (
        HTML_TEMPLATE.replace("__LABELS__", json.dumps(labels))
        .replace("__PROJECTED_HOURS__", json.dumps(projected))
        .replace("__ACTUAL_HOURS__", json.dumps(actual))
        .replace("__TOTAL_SAVED_HOURS__", json.dumps(total_saved))
        .replace("__STAR_METRICS__", json.dumps(star_metrics))
        .replace("__SITUATION_TEXT__", star_metrics["situation_text"])
        .replace("__TASK_TEXT__", star_metrics["task_text"])
        .replace("__ACTION_TEXT__", star_metrics["action_text"])
        .replace("__RESULT_TEXT__", star_metrics["result_text"])
    )

    output_file.write_text(html, encoding="utf-8")
    return output_file


def main() -> None:
    output_path = Path(__file__).resolve().parent / "live_impact_dashboard.html"
    generated = generate_dashboard(output_path)
    print(f"Live dashboard generated at: {generated}")


if __name__ == "__main__":
    main()
