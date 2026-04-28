"""Compatibility wrapper for the installable public package."""

from global_impact_tracker.dashboard import *  # noqa: F401,F403
from global_impact_tracker.dashboard import main


if __name__ == "__main__":
    main()
