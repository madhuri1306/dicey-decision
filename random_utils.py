import random

def resolve_tie(options, method):
    if not options:
        return None
    if method == "dice":
        return random.choice(options)  # Simulates dice roll
    elif method == "spinner":
        return random.choice(options)  # Simulates spinner
    elif method == "coin":
        return random.choice(options)  # Simulates coin flip
    return random.choice(options)  # Fallback