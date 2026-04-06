import json
import os
import sys
from pathlib import Path

from google import genai as genai_sdk
from google.genai import types as genai_types
from mcp.server.fastmcp import FastMCP

# Validate and insert IMPACT_TRACKER_PATH before local import
_tracker_path = os.environ.get(
    "IMPACT_TRACKER_PATH",
    str(Path(__file__).parent.parent / "core")
)
_tracker_path_obj = Path(_tracker_path).resolve()

if not _tracker_path_obj.is_dir():
    raise RuntimeError(
        f"IMPACT_TRACKER_PATH is not a valid directory: {_tracker_path_obj}\n"
        "Check your mcp_config.json env block."
    )
if not (_tracker_path_obj / "tracker.py").exists():
    raise RuntimeError(
        f"tracker.py not found in IMPACT_TRACKER_PATH: {_tracker_path_obj}\n"
        "Ensure IMPACT_TRACKER_PATH points to the core/ directory."
    )

sys.path.insert(0, str(_tracker_path_obj))

from tracker import GlobalImpactTracker  # noqa: E402
from entitlements import is_pro  # noqa: E402

# Init
mcp = FastMCP("global-impact-tracker")
tracker = GlobalImpactTracker()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
_genai_client = genai_sdk.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


def _estimate_with_gemini(task: str, context: str) -> dict:
    """Call Gemini 2.5 Flash to estimate baseline hours and AI seconds from task context."""
    prompt = f"""You are estimating engineering productivity metrics.

Task: {task}
Context: {context}

Estimate:
1. baseline_hours: How many hours a senior engineer would take to do this manually (be realistic)
2. ai_seconds: How many seconds an AI assistant likely took based on the context described

Return JSON with keys: baseline_hours (float), ai_seconds (float), reasoning (string, one sentence)."""

    response = _genai_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=genai_types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=256,
            response_mime_type="application/json",
        ),
    )
    return json.loads(response.text)


@mcp.tool()
def log_task(
    project: str,
    task: str,
    context: str,
    status: str = "Success",
    baseline_hours: float = None,
    ai_seconds: float = None,
    task_type: str = None,
    complexity: str = None,
    tools_used: str = None,
    dollars_saved: float = None,
    audience: str = None,
    token_usage: int = None,
) -> str:
    """Log a completed task. Provide project, task description, and context of what happened.
    If baseline_hours and ai_seconds are not provided, Gemini will estimate them from context.
    Optional: task_type (feature|bug|refactor|review), complexity (low|medium|high),
    tools_used (pipe-separated e.g. claude|windsurf), dollars_saved (override auto-compute),
    audience (self|manager|recruiter), token_usage (LLM tokens consumed)."""

    if baseline_hours is None or ai_seconds is None:
        if not GEMINI_API_KEY or not is_pro():
            return (
                "Pro tier required for AI estimation. Provide baseline_hours and "
                "ai_seconds manually, or upgrade at https://buy.stripe.com/eVqcN45Xg2iJ3VXaFM0Ny03"
            )
        estimates = _estimate_with_gemini(task, context)
        baseline_hours = baseline_hours or estimates["baseline_hours"]
        ai_seconds = ai_seconds or estimates["ai_seconds"]
        reasoning = estimates.get("reasoning", "")
    else:
        reasoning = "Manual override — values provided directly."

    tracker.log_impact(
        project,
        task,
        baseline_hours,
        ai_seconds,
        status,
        task_type=task_type,
        complexity=complexity,
        tools_used=tools_used,
        dollars_saved=dollars_saved,
        audience=audience,
        token_usage=token_usage,
    )

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
def generate_star_story(audience: str = "self") -> str:
    """Generate a formatted STAR narrative from live tracker data using Gemini.
    audience: 'self' (default), 'manager' (formal, outcome-focused), or 'recruiter' (punchy, metrics-forward)."""
    snap = tracker.capture_metrics_snapshot()
    dashboard = get_dashboard_data()

    if not GEMINI_API_KEY or not is_pro():
        hours_saved = snap.get("total_hours_saved", 0)
        projects = snap.get("projects_count", 0)
        tasks = snap.get("queries_processed", 0)
        rate = snap.get("latency_reduction_pct", 0)

        return (
            f"**STAR Impact Story** _(free tier — upgrade for AI-generated narrative)_\n\n"
            f"**Situation:** Engineering workflows required significant manual effort across "
            f"{projects} active projects.\n"
            f"**Task:** Reduce time-to-delivery by integrating AI orchestration into the "
            f"development loop.\n"
            f"**Action:** Logged {tasks} AI-assisted tasks, replacing manual execution with "
            f"automated AI pipelines tracked in real time.\n"
            f"**Result:** Saved {hours_saved:.1f} hours ({rate:.0f}% latency reduction) vs "
            f"manual baseline.\n\n"
            f"Upgrade to Pro for a Gemini-generated narrative tailored to your audience: "
            f"https://buy.stripe.com/eVqcN45Xg2iJ3VXaFM0Ny03"
        )

    tone_directive = {
        "manager": "Write formally. Emphasize business outcomes, reliability, and team impact. Avoid jargon.",
        "recruiter": "Write punchy and metrics-forward. Lead with numbers. Optimized for a resume or LinkedIn summary.",
    }.get(audience, "Write conversationally for a self-review or personal reflection.")

    prompt = f"""Audience: {audience}
Tone directive: {tone_directive}

Metrics snapshot:
{json.dumps(snap, indent=2)}

Project breakdown:
{json.dumps(dashboard, indent=2)}

Write a compelling, specific STAR story (Situation, Task, Action, Result) using the real numbers above.
Keep it under 200 words. Use bold headers for each section. Lead with impact."""

    response = _genai_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=genai_types.GenerateContentConfig(
            temperature=0.7,
            top_p=0.95,
            max_output_tokens=512,
            system_instruction=(
                "You are a technical writing assistant specializing in engineer performance narratives. "
                "Always use the exact numbers provided. Never fabricate metrics."
            ),
        ),
    )
    return response.text.strip()


if __name__ == "__main__":
    mcp.run(transport="stdio")