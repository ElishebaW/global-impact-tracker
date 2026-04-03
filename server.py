import json
import os
import sys
from pathlib import Path

import google.generativeai as genai
from mcp.server.fastmcp import FastMCP

# Path must be set before local import
sys.path.insert(0, os.environ.get(
    "IMPACT_TRACKER_PATH",
    str(Path(__file__).parent.parent / "global_impact_tracker/orchestration_insights/app")
))

from tracker import GlobalImpactTracker  # noqa: E402

# Init
mcp = FastMCP("global-impact-tracker")
tracker = GlobalImpactTracker()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def _estimate_with_gemini(task: str, context: str) -> dict:
    """Call Gemini 2.5 Flash to estimate baseline hours and AI seconds from task context."""
    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = f"""You are estimating engineering productivity metrics.

Task: {task}
Context: {context}

Estimate:
1. baseline_hours: How many hours a senior engineer would take to do this manually (be realistic)
2. ai_seconds: How many seconds an AI assistant likely took based on the context described

Respond with ONLY valid JSON, no markdown:
{{"baseline_hours": <float>, "ai_seconds": <float>, "reasoning": "<one sentence>"}}"""

    response = model.generate_content(prompt)
    return json.loads(response.text.strip())


@mcp.tool()
def log_task(
    project: str,
    task: str,
    context: str,
    status: str = "Success",
    baseline_hours: float = None,
    ai_seconds: float = None,
) -> str:
    """Log a completed task. Provide project, task description, and context of what happened.
    If baseline_hours and ai_seconds are not provided, Gemini will estimate them from context."""

    if baseline_hours is None or ai_seconds is None:
        if not GEMINI_API_KEY:
            return "Error: GEMINI_API_KEY not set and no baseline_hours/ai_seconds provided."
        estimates = _estimate_with_gemini(task, context)
        baseline_hours = baseline_hours or estimates["baseline_hours"]
        ai_seconds = ai_seconds or estimates["ai_seconds"]
        reasoning = estimates.get("reasoning", "")
    else:
        reasoning = "Manual override — values provided directly."

    tracker.log_impact(project, task, baseline_hours, ai_seconds, status)

    return (
        f"Logged: [{project}] {task}\n"
        f"  Baseline: {baseline_hours}h | AI: {ai_seconds}s | Status: {status}\n"
        f"  Estimate reasoning: {reasoning}"
    )


@mcp.tool()
def get_metrics() -> dict:
    """Return current STAR metrics snapshot. Reads live data from the tracker CSV."""
    return tracker.capture_metrics_snapshot()


@mcp.tool()
def get_dashboard_data() -> dict:
    """Return aggregated stats per project for dashboard or reporting consumption."""
    rows = tracker._read_rows()
    projects = {}
    for r in rows:
        p = r["Project"]
        if p not in projects:
            projects[p] = {"tasks": 0, "baseline_hrs": 0.0, "ai_hrs": 0.0, "successes": 0}
        projects[p]["tasks"] += 1
        projects[p]["baseline_hrs"] += tracker._to_float(r["Human_Baseline_Hrs"])
        projects[p]["ai_hrs"] += tracker._to_float(r["AI_Sec"]) / 3600
        if r.get("Status", "").lower() == "success":
            projects[p]["successes"] += 1

    for p in projects:
        b = projects[p]["baseline_hrs"]
        a = projects[p]["ai_hrs"]
        projects[p]["hours_saved"] = round(b - a, 4)
        projects[p]["latency_reduction_pct"] = round((b - a) / b * 100, 1) if b > 0 else 0

    return projects


@mcp.tool()
def generate_star_story() -> str:
    """Generate a formatted STAR narrative from live tracker data using Gemini."""
    snap = tracker.capture_metrics_snapshot()

    dashboard = get_dashboard_data()

    if not GEMINI_API_KEY:
        hours_saved = snap.get("total_hours_saved", 0)
        projects = snap.get("projects_count", 0)
        tasks = snap.get("queries_processed", 0)
        rate = snap.get("latency_reduction_pct", 0)

        return (
            f"**STAR Impact Story**\n"
            f"**Situation:** Engineering workflows required significant manual effort across "
            f"{projects} active projects.\n"
            f"**Task:** Reduce time-to-delivery by integrating AI orchestration into the "
            f"development loop.\n"
            f"**Action:** Logged {tasks} AI-assisted tasks, replacing manual execution with "
            f"automated AI pipelines tracked in real time.\n"
            f"**Result:** Saved {hours_saved:.1f} hours ({rate:.0f}% latency reduction) vs "
            f"manual baseline."
        )

    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = f"""You are writing a STAR format performance story for an engineer's self-review.

Metrics snapshot:
{json.dumps(snap, indent=2)}

Project breakdown:
{json.dumps(dashboard, indent=2)}

Write a compelling, specific STAR story (Situation, Task, Action, Result) using the real numbers above.
Keep it under 200 words. Use bold headers for each section. Lead with impact."""

    response = model.generate_content(prompt)
    return response.text.strip()


if __name__ == "__main__":
    mcp.run(transport="stdio")
