import re

def validate_email(email: str) -> bool:
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email)) 