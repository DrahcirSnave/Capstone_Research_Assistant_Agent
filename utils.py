import json
import os

MEMORY_FILE = "memory.json"
DEFAULT_CONFIG = "config.json"

def load_memory():
    """Loads user preferences from JSON, creating defaults if missing."""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    elif os.path.exists(DEFAULT_CONFIG):
        with open(DEFAULT_CONFIG, "r") as f:
            data = json.load(f)
            # Create the memory file for read/write operations
            with open(MEMORY_FILE, "w") as out:
                json.dump(data, out, indent=4)
            return data
    else:
        # Hard fallback
        return {"preferred_summary_length": 150, "credibility_priority": "medium"}

def update_memory(key, value):
    """Updates a specific key in the persistent memory file."""
    memory = load_memory()
    memory[key] = value
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)

def safety_check(query):
    """
    Screens input for harmful terms.
    Returns False if banned words are found.
    """
    banned = ["how to make a bomb", "suicide", "harm", "weapons", "kill"]
    lower = query.lower()
    for b in banned:
        if b in lower:
            return False
    return True

def evaluate_source(url):
    """
    Heuristic to rate the trustworthiness of a URL.
    """
    if "edu" in url:
        return "High credibility (.edu)"
    if "gov" in url:
        return "High credibility (.gov)"
    if "org" in url:
        return "Medium credibility (.org)"
    return "Low credibility"

def apply_feedback(feedback):
    """
    Reinforcement Learning Mechanism:
    Adjusts summary length preference based on user feedback.
    """
    memory = load_memory()
    current_length = memory.get("preferred_summary_length", 150)
    
    if feedback == "too long":
        new_len = max(80, current_length - 30)
        update_memory("preferred_summary_length", new_len)
    elif feedback == "too short":
        new_len = min(400, current_length + 30)
        update_memory("preferred_summary_length", new_len)
