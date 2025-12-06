import json
import os

MEMORY_FILE = "memory.json"
DEFAULT_CONFIG = "config.json"

def load_memory():
    """
    Loads user preferences from memory.json.
    If memory.json doesn't exist, it creates it using defaults from config.json.
    """
    # 1. Try to load the existing memory file
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            # If file is corrupted, ignore it and fall through to default
            pass

    # 2. If memory missing/corrupt, load defaults from config
    if os.path.exists(DEFAULT_CONFIG):
        with open(DEFAULT_CONFIG, "r") as f:
            data = json.load(f)
            # Create the memory file for future read/write operations
            with open(MEMORY_FILE, "w") as out:
                json.dump(data, out, indent=4)
            return data
            
    # 3. Hard fallback if both files are missing
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
    if not url:
        return "Unknown Source"
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
        # Shorten by 30 tokens, but don't go below 80
        new_len = max(80, current_length - 30)
        update_memory("preferred_summary_length", new_len)
    elif feedback == "too short":
        # Lengthen by 30 tokens, but don't go above 400
        new_len = min(400, current_length + 30)
        update_memory("preferred_summary_length", new_len)
    elif feedback == "good":
        # No change needed, but we could log this success in a future version
        pass
