# phase/constants.py

PHASE_ALIASES = {
    "engage": "Engage",
    "investigate": "Investigate",
    "act": "Act",
    "Engage": "Engage",
    "Investigate": "Investigate",
    "Act": "Act",
}

VALID_PHASES = set(PHASE_ALIASES.values())

STEP_MAP = {
    "Engage": ["big_idea", "essential_question", "challenge"],
    "Investigate": ["guiding_question", "activities_resources", "synthesis"],
    "Act": ["solution", "implementation", "evaluation"],
}

PHASE_POSITION = {
    "Engage": 1,
    "Investigate": 2,
    "Act": 3,
}

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