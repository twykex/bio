def calculate_bmi(weight_kg, height_m):
    try:
        return f"BMI: {float(weight_kg) / (float(height_m) ** 2):.2f}"
    except Exception:
        return "Error."


def estimate_daily_calories(weight_kg, height_cm=170, age=30, gender="male", activity_level="sedentary"):
    try:
        weight = float(weight_kg)
        height = float(height_cm)
        age = float(age)

        # Mifflin-St Jeor Equation
        bmr = 10 * weight + 6.25 * height - 5 * age
        if gender.lower().startswith('m'):
            bmr += 5
        else:
            bmr -= 161

        multipliers = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "extreme": 1.9
        }

        # Simple fuzzy matching for activity
        act = activity_level.lower()
        multiplier = 1.2
        for key, val in multipliers.items():
            if key in act:
                multiplier = val
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
