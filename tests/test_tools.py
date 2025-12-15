import unittest
from services.tools import calculate_bmi, estimate_daily_calories

class TestTools(unittest.TestCase):
    def test_calculate_bmi(self):
        # 70kg, 1.75m -> 22.86
        result = calculate_bmi(70, 1.75)
        self.assertIn("BMI: 22.86", result)

    def test_calculate_bmi_error(self):
        result = calculate_bmi("weight", 1.75)
        self.assertIn("Error", result)

    def test_estimate_daily_calories(self):
        # Male, 70kg, 175cm, 30y, Moderate (1.55)
        # BMR = 10*70 + 6.25*175 - 5*30 + 5 = 700 + 1093.75 - 150 + 5 = 1648.75
        # TDEE = 1648.75 * 1.55 = 2555.56
        # Expected result string format: "TDEE: 2556 kcal"
        result = estimate_daily_calories(weight_kg=70, height_cm=175, age=30, gender="male", activity_level="moderate")
        self.assertIn("TDEE: 2556", result)

    def test_estimate_daily_calories_female(self):
        # Female, 60kg, 160cm, 25y, Sedentary (1.2)
        # BMR = 10*60 + 6.25*160 - 5*25 - 161 = 600 + 1000 - 125 - 161 = 1314
        # TDEE = 1314 * 1.2 = 1576.8
        result = estimate_daily_calories(weight_kg=60, height_cm=160, age=25, gender="female", activity_level="sedentary")
        self.assertIn("TDEE: 1577", result)

if __name__ == '__main__':
    unittest.main()
