import json
import re
import logging

logger = logging.getLogger(__name__)

def clean_json_output(text):
    """
    STACK-BASED CLEANER: Finds the first valid JSON object or array
    and stops exactly when it closes. Ignores trailing text.
    Handles nested objects and strings correctly.
    """
    text = text.strip()

    # Locate the first possible start of JSON
    start_idx = -1
    for i, char in enumerate(text):
        if char in ['{', '[']:
            start_idx = i
            break

    if start_idx == -1:
        return text  # No JSON found

    # Stack counting
    stack = []
    in_string = False
    escape = False

    for i in range(start_idx, len(text)):
        char = text[i]

        if in_string:
            if char == '"' and not escape:
                in_string = False

            if char == '\\' and not escape:
                escape = True
            else:
                escape = False
        else:
            if char == '"':
                in_string = True
            elif char in ['{', '[']:
                stack.append(char)
            elif char in ['}', ']']:
                if not stack:
                    break  # Error: unbalanced

                # Check for matching pair
                last = stack[-1]
                if (last == '{' and char == '}') or (last == '[' and char == ']'):
                    stack.pop()

                # If stack is empty, we found the full object!
                if not stack:
                    return text[start_idx: i + 1]

    return text[start_idx:]  # Fallback


def repair_lazy_json(text):
    text = re.sub(r'("day":\s*"[^"]+",\s*)("[^"]+")(\s*,)', r'\1"title": \2\3', text)
    text = re.sub(r'(,\s*)("[^"]+")(\s*\})', r'\1"desc": \2\3', text)
    return text


def fix_truncated_json(json_str):
    json_str = json_str.strip()
    # 1. Strip trailing comma
    json_str = re.sub(r',\s*$', '', json_str)

    # 2. Balance Quotes
    quote_count = 0
    escape = False
    for char in json_str:
        if char == '"' and not escape:
            quote_count += 1

        if char == '\\' and (quote_count % 2 == 1):
             escape = not escape
        else:
             escape = False

    if quote_count % 2 == 1:
        json_str += '"'

    # 3. Handle orphaned keys and colons
    s = json_str.strip()
    if s.endswith(':'):
        json_str += ' null'

    # Check if we ended on a key (string without colon in object)
    # Re-scan to build stack
    stack = []
    in_string = False
    escape = False

    for char in json_str:
        if char == '"' and not escape:
            in_string = not in_string

        if not in_string:
            if char == '{': stack.append('}')
            elif char == '[': stack.append(']')
            elif char == '}' or char == ']':
                if stack and stack[-1] == char:
                    stack.pop()

        if char == '\\' and in_string:
            escape = not escape
        else:
            escape = False

    if stack and stack[-1] == '}':
        # In object, check if last token is a key
        idx = len(json_str) - 1
        while idx >= 0 and json_str[idx].isspace():
            idx -= 1

        if idx >= 0 and json_str[idx] == '"':
            # Find start of string
            idx -= 1
            while idx >= 0:
                if json_str[idx] == '"' and (idx == 0 or json_str[idx-1] != '\\'):
                    break
                idx -= 1

            # Check char before string
            idx -= 1
            while idx >= 0 and json_str[idx].isspace():
                idx -= 1

            if idx >= 0 and json_str[idx] in [',', '{']:
                json_str += ': null'

    # 4. Close Stack
    while stack:
        json_str += stack.pop()

    return json_str


def remove_json_comments(text):
    output = []
    in_string = False
    escape = False
    i = 0
    while i < len(text):
        char = text[i]
        if in_string:
            if char == '"' and not escape:
                in_string = False
            if char == '\\' and not escape:
                escape = True
            else:
                escape = False
            output.append(char)
            i += 1
        else:
            if char == '"':
                in_string = True
                output.append(char)
                i += 1
            elif char == '/' and i + 1 < len(text) and text[i+1] == '/':
                i += 2
                while i < len(text) and text[i] != '\n':
                    i += 1
            else:
                output.append(char)
                i += 1
    return "".join(output)


def clean_and_parse_json(text):
    # 1. Use stack-based extractor to isolate JSON block
    cleaned = clean_json_output(text)

    # 2. Fix specific lazy patterns
    cleaned = repair_lazy_json(cleaned)
    cleaned = remove_json_comments(cleaned)

    # 3. Fix common syntax errors
    cleaned = re.sub(r'\]\s*"\s*\}', '] }', cleaned)
    cleaned = re.sub(r',\s*\}', '}', cleaned)
    cleaned = re.sub(r',\s*\]', ']', cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        logger.warning("JSON Invalid. Attempting auto-balance...")
        balanced = fix_truncated_json(cleaned)
        try:
            return json.loads(balanced)
        except json.JSONDecodeError:
            return None
