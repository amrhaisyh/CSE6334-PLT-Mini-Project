import re

# Define token patterns
TOKEN_PATTERNS = {
    "EVENT": r"on|schedule|if|repeat|activate",
    "SENSOR": r"motion|temperature|humidity|door|sound",  # Removed "light" from here
    "DEVICE": r"lights|AC|fan|door|alarm|sprinkler|watering",  # "lights" remains here
    "OPERATION": r"turn on|turn off|increase|decrease|open|close|start|check",
    "MODE": r"night mode|vacation mode|silent mode",
    "TIME": r"\d{1,2}:\d{2} (AM|PM)",
    "TIME_INTERVAL": r"\d+ (seconds|minutes|hours)",
    "NUMBER": r"\d+",
    "OPERATOR": r">|<|>=|<=|==",
    "THEN": r"then",
    "FROM_TO": r"from|to",
    "DETECTED": r"detected",
    "AT": r"at",
    "EVERY": r"every"
}

# Combine token patterns
TOKEN_REGEX = re.compile(
    "|".join(f"(?P<{key}>{pattern})" for key, pattern in TOKEN_PATTERNS.items()), re.IGNORECASE
)

# Tokenizer function
def tokenize(command):
    tokens = []
    for match in TOKEN_REGEX.finditer(command):
        token_type = match.lastgroup
        value = match.group(token_type)
        tokens.append((token_type, value))
    return tokens

# Syntax validation function
def validate_syntax(tokens):
    if not tokens:
        return False, "Empty command."
    
    first_token = tokens[0][1]
    if first_token == "on":
        return validate_event(tokens)
    elif first_token == "schedule":
        return validate_schedule(tokens)
    elif first_token == "if":
        return validate_condition(tokens)
    elif first_token == "repeat":
        return validate_loop(tokens)
    elif first_token == "activate":
        return validate_mode(tokens)
    else:
        return False, "Invalid command start."

# Specific validation functions
def validate_event(tokens):
    pattern = ["EVENT", "SENSOR", "DETECTED", "THEN", "OPERATION", "DEVICE"]
    return match_pattern(tokens, pattern)

def validate_schedule(tokens):
    pattern = ["EVENT", "OPERATION", "DEVICE", "AT", "TIME"]
    return match_pattern(tokens, pattern)

def validate_condition(tokens):
    pattern = ["EVENT", "SENSOR", "OPERATOR", "NUMBER", "THEN", "OPERATION", "DEVICE"]
    return match_pattern(tokens, pattern)

def validate_loop(tokens):
    pattern = ["EVENT", "OPERATION", "SENSOR", "EVERY", "TIME_INTERVAL"]
    return match_pattern(tokens, pattern)

def validate_mode(tokens):
    pattern = ["EVENT", "MODE", "FROM_TO", "TIME", "FROM_TO", "TIME"]
    return match_pattern(tokens, pattern)

def match_pattern(tokens, expected_pattern):
    extracted_types = [t[0] for t in tokens]
    if extracted_types == expected_pattern:
        return True, "Valid command."
    return False, "Syntax error in command."

# Invalid command validation functions
def validate_invalid_command(command, tokens):
    # Check if "when" is used instead of "on"
    if "when" in command:
        return f"Error: 'when' is not a valid keyword. Correct syntax: 'on motion detected then turn on lights'."
    
    # Check if 'then' is missing in conditions (e.g., "if temperature > 30 start AC")
    if "if" in command and "then" not in [t[0] for t in tokens]:
        return "Error: The 'then' keyword is required before 'start AC'."
    
    # Check for invalid operation like "open lights"
    if "open" in [t[0] for t in tokens] and "light" in [t[0] for t in tokens]:
        return "Error: 'open lights' is not a valid action. The correct operation is 'turn on lights'."
    
    # Check for incorrect time format
    if "PM" in command and re.search(r"\d{1,2}:\d{2} PM", command) and not re.match(r"(\d{1,2}):([0-5][0-9]) PM", command):
        return "Error: Minutes must be between 00-59."
    
    # Check if 'from' and 'to' are missing for mode activation
    if "from" not in command or "to" not in command:
        return "Error: The 'from' and 'to' keywords are missing. Correct syntax: 'activate silent mode from 10 PM to 6 AM'."
    
    return "Error: Invalid command."

# Example test cases for valid and invalid commands
commands = [
    "on motion detected then turn on lights",
    "schedule turn on watering at 6:00 AM",
    "if temperature > 30 then turn on AC",
    "repeat check temperature every 10 minutes",
    "activate night mode from 10:00 PM to 6:00 AM",
    # Invalid commands
    "when motion detected turn on lights",
    "if temperature > 30 start AC",
    "on humidity triggered then open lights",
    "schedule cooling at 14:99 PM",
    "activate silent mode 10 PM 6 AM"
]

for cmd in commands:
    tokens = tokenize(cmd)
    valid, message = validate_syntax(tokens)
    if valid:
        print(f"Command: {cmd}\nTokens: {tokens}\nValidation: {message}\n")
    else:
        error_message = validate_invalid_command(cmd, tokens)
        print(f"Command: {cmd}\nTokens: {tokens}\n{error_message}\nValidation: Invalid command.\n")
