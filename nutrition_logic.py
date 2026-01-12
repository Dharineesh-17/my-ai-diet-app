def calculate_bmr(weight, height, age, gender):
    if gender.lower() == "male":
        return (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        return (10 * weight) + (6.25 * height) - (5 * age) - 161

def calculate_tdee(bmr, activity_level):
    # TDEE is Total Daily Energy Expenditure (Calories burned with exercise)
    rates = {
        "sedentary": 1.2,        # Little to no exercise
        "moderate": 1.55,       # Exercise 3-5 days/week
        "active": 1.725         # Heavy exercise 6-7 days/week
    }
    return bmr * rates.get(activity_level, 1.2)

# --- TEST IT ---
# Let's test with a 25 year old male, 80kg, 180cm
user_bmr = calculate_bmr(80, 180, 25, "male")
user_tdee = calculate_tdee(user_bmr, "moderate")

print(f"Your body burns {user_bmr:.0f} calories at rest.")
print(f"To maintain weight with moderate exercise, you need {user_tdee:.0f} calories.")