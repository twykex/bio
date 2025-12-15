def calculate_bmi(weight_kg, height_m):
    try:
        w = float(weight_kg)
        h = float(height_m)
        # Unit correction: if height is > 3.0, assume it's cm and convert to m
        if h > 3.0:
            h = h / 100.0
        return f"BMI: {w / (h ** 2):.2f}"
    except Exception:
        return "Error."


def estimate_daily_calories(weight_kg, height_cm=170, age=30, gender="male", activity_level="sedentary"):
    try:
        weight = float(weight_kg)
        height = float(height_cm)
        age = float(age)

        # Unit correction: if height is < 3.0, assume it's m and convert to cm
        if height < 3.0:
            height = height * 100.0

        # Mifflin-St Jeor Equation
        bmr = 10 * weight + 6.25 * height - 5 * age
        if gender.lower().startswith('m'):
            bmr += 5
        else:
            bmr -= 161

        multipliers = {
            "sedentary": 1.2,
            "light": 1.375,
            "lightly": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "extreme": 1.9
        }

        # Simple fuzzy matching for activity
        act = activity_level.lower()
        multiplier = 1.2
        # Sort keys by length descending to match "extremely active" to "extreme" before "active"
        for key in sorted(multipliers.keys(), key=len, reverse=True):
            if key in act:
                multiplier = multipliers[key]
                break

        tdee = int(bmr * multiplier)
        return f"BMR: {int(bmr)} kcal | TDEE: {tdee} kcal"
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
