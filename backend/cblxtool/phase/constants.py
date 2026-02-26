# phase/constants.py

PHASE_ALIASES = {
    "engage": "Engage",
    "investigate": "Investigate",
    "act": "Act",
    "essentialquestioning": "EssentialQuestioning",
    "Engage": "Engage",
    "Investigate": "Investigate",
    "Act": "Act",
    "EssentialQuestioning": "EssentialQuestioning",
}

VALID_PHASES = set(PHASE_ALIASES.values())

STEP_MAP = {
    "Engage": ["big_idea", "challenge"],
    "EssentialQuestioning": ["questions", "selected_question"],
    "Investigate": ["guiding_question", "activities_resources", "synthesis"],
    "Act": ["solution", "implementation", "evaluation"],
}

PHASE_POSITION = {
    "Engage": 1,
    "EssentialQuestioning": 2, 
    "Investigate": 3,
    "Act": 4,
}

DEFAULT_DYNAMIC_DATA = {
    "Engage": {
        "big_idea": [{"content": ""}],
        "challenge": [{"content": ""}],
    },
    "EssentialQuestioning": {
        "questions": [""],
        "selected_question": "",
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