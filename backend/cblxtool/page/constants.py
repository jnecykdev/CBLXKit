# page/constants.py
from datetime import timedelta

VALID_PHASES = {"Engage", "Investigate", "Act"}

DEFAULT_DYNAMIC_DATA = {
    "Engage": {
        "big_idea": [{"content": ""}],
        "essential_question": [{"content": ""}],
        "challenge": [{"content": ""}],
    },
    "Investigate": {
        "guiding_questions": [{"content": ""}],
        "activities_resources": [{"content": ""}],
        "synthesis": [{"content": ""}],
    },
    "Act": {
        "solution": [{"content": ""}],
        "implementation": [{"content": ""}],
        "evaluation": [{"content": ""}],
    },
}

MAX_PAGES_PER_PHASE = 5

LOCK_TTL = timedelta(minutes=30)