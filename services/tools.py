import logging

logger = logging.getLogger(__name__)

def calculate_bmi(weight_kg, height_m):
    try:
        bmi = float(weight_kg) / (float(height_m) ** 2)
        return f"BMI: {bmi:.2f}"
    except (TypeError, ValueError, ZeroDivisionError) as e:
        logger.error(f"BMI Calculation Error: {e}")
        return "Error: Invalid input."


def estimate_daily_calories(weight_kg, height_cm, age, gender="male", activity_level="sedentary"):
    try:
        w = float(weight_kg)
        h = float(height_cm)
        a = int(age)

        # Mifflin-St Jeor Equation
        bmr = 10 * w + 6.25 * h - 5 * a
        if gender.lower() == "female":
            bmr -= 161
        else:
            bmr += 5

        multipliers = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "athlete": 1.9
        }

        # Fuzzy match for activity level
        level = activity_level.lower()
        multiplier = 1.2 # Default

        # Check against keys
        if level in multipliers:
            multiplier = multipliers[level]
        else:
            # Try to find substring match
            for key, val in multipliers.items():
                if key in level:
                    multiplier = val
                    break

        tdee = int(round(bmr * multiplier))
        return f"TDEE: {tdee} kcal"
    except Exception as e:
        logger.error(f"Calories Calculation Error: {e}")
        return "Error: Invalid input."


AVAILABLE_TOOLS = {"calculate_bmi": calculate_bmi, "estimate_daily_calories": estimate_daily_calories}


def execute_tool_call(tool, args):
    if tool in AVAILABLE_TOOLS:
        try:
            return AVAILABLE_TOOLS[tool](**args)
        except Exception as e:
            logger.error(f"Tool Execution Error: {e}")
            return f"Tool Error: {e}"
    return "Unknown Tool"
