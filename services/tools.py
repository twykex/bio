def calculate_bmi(weight_kg, height_m):
    try:
        return f"BMI: {float(weight_kg) / (float(height_m) ** 2):.2f}"
    except Exception:
        return "Error."


def estimate_daily_calories(weight_kg, activity_level="sedentary"):
    try:
        return f"TDEE: {int(10 * float(weight_kg) + 6.25 * 170 - 5 * 30 + 5)} kcal"
    except Exception:
        return "Error."


AVAILABLE_TOOLS = {"calculate_bmi": calculate_bmi, "estimate_daily_calories": estimate_daily_calories}


def execute_tool_call(tool, args):
    if tool in AVAILABLE_TOOLS:
        try:
            return AVAILABLE_TOOLS[tool](**args)
        except Exception:
            return "Tool Error"
    return "Unknown Tool"
