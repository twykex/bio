export const dailyTips = [
    "Hydration increases energy levels by up to 20%.",
    "Walking 10 mins after meals lowers blood sugar spikes.",
    "Magnesium helps muscle recovery and sleep quality.",
    "Cold showers can boost dopamine by 250%.",
    "Morning sunlight sets your circadian rhythm for better sleep.",
    "Eating protein for breakfast reduces cravings later.",
    "7-8 hours of sleep is the best performance enhancer.",
    "Fiber feeds your gut microbiome, boosting immunity."
];

export const quickPrompts = ['Does this meal plan have enough protein?', 'Can you swap Tuesday dinner?', 'I am feeling tired today.', 'Suggest a healthy snack.'];

export const toolsList = [
    { id: 'symptom_checker', category: 'Wellness', name: 'Symptom Checker', desc: 'Check symptoms with AI.', inputs: [{k:'symptoms', l:'Describe Symptoms', p:'Headache and fatigue'}] },
    { id: 'suggest_supplement', category: 'Wellness', name: 'Supplement Advisor', desc: 'Get supplement recommendations.', inputs: [{k:'focus', l:'Focus', p:'Joint Health', options: ['Joint Health', 'Energy', 'Sleep', 'Immunity', 'Stress', 'Digestion']}] },
    { id: 'check_food_interaction', category: 'Nutrition', name: 'Interaction Checker', desc: 'Check if foods clash.', inputs: [{k:'item1', l:'Item A', p:'Grapefruit'}, {k:'item2', l:'Item B', p:'Medication'}] },
    { id: 'recipe_variation', category: 'Nutrition', name: 'Recipe Variator', desc: 'Modify a recipe.', inputs: [{k:'recipe', l:'Original Recipe', p:'Lasagna'}, {k:'type', l:'Variation Type', p:'Keto', options: ['Keto', 'Vegan', 'Paleo', 'Low-Carb', 'Gluten-Free']}] },
    { id: 'flavor_pairing', category: 'Nutrition', name: 'Flavor Pairer', desc: 'Find matching flavors.', inputs: [{k:'ingredient', l:'Ingredient', p:'Salmon'}] },
    { id: 'quick_snack', category: 'Nutrition', name: 'Snack Generator', desc: 'Get a quick snack idea.', inputs: [{k:'preference', l:'Preference', p:'Savory', options: ['Savory', 'Sweet', 'Crunchy', 'High Protein', 'Low Calorie']}] },
    { id: 'hydration_tip', category: 'Wellness', name: 'Hydration Coach', desc: 'Tips for hydration.', inputs: [{k:'activity', l:'Activity Level', p:'High Intensity', options: ['Sedentary', 'Light Activity', 'Moderate Activity', 'High Intensity', 'Athlete']}] },
    { id: 'mood_food', category: 'Nutrition', name: 'Mood Food', desc: 'Food for your mood.', inputs: [{k:'mood', l:'Current Mood', p:'Stressed', options: ['Stressed', 'Happy', 'Sad', 'Anxious', 'Tired', 'Energetic']}] },
    { id: 'energy_booster', category: 'Wellness', name: 'Energy Booster', desc: 'Natural energy sources.', inputs: [{k:'context', l:'Context', p:'Afternoon Slump', options: ['Morning', 'Afternoon Slump', 'Pre-Workout', 'Late Night']}] },
    { id: 'recovery_meal', category: 'Performance', name: 'Recovery Meal', desc: 'Post-workout fuel.', inputs: [{k:'workout', l:'Workout Type', p:'Heavy Lifting', options: ['Heavy Lifting', 'Cardio', 'HIIT', 'Yoga', 'Sports']}] },
    { id: 'sleep_aid', category: 'Wellness', name: 'Sleep Aid', desc: 'Foods to help sleep.', inputs: [{k:'issue', l:'Sleep Issue', p:'Trouble Falling Asleep', options: ['Trouble Falling Asleep', 'Waking Up Frequently', 'Light Sleeper', 'Insomnia']}] },
    { id: 'digestive_aid', category: 'Wellness', name: 'Digestive Helper', desc: 'Foods for digestion.', inputs: [{k:'symptom', l:'Symptom', p:'Bloating', options: ['Bloating', 'Indigestion', 'Nausea', 'Heartburn', 'Constipation']}] },
    { id: 'immunity_booster', category: 'Wellness', name: 'Immunity Boost', desc: 'Boost your immune system.', inputs: [{k:'season', l:'Season/Context', p:'Flu Season', options: ['Flu Season', 'Winter', 'Spring', 'Traveling', 'Stressful Period']}] },
    { id: 'anti_inflammatory', category: 'Wellness', name: 'Inflammation Fighter', desc: 'Reduce inflammation.', inputs: [{k:'condition', l:'Concern', p:'General', options: ['General', 'Joint Pain', 'Gut Health', 'Skin Issues', 'Headaches']}] },
    { id: 'antioxidant_rich', category: 'Wellness', name: 'Antioxidant Finder', desc: 'Find rich foods.', inputs: [{k:'preference', l:'Preference', p:'Berries', options: ['Berries', 'Vegetables', 'Nuts', 'Teas', 'Spices']}] },
    { id: 'low_gi_option', category: 'Nutrition', name: 'Low GI Swap', desc: 'Stable blood sugar.', inputs: [{k:'food', l:'High GI Food', p:'White Rice'}] },
    { id: 'high_protein_option', category: 'Nutrition', name: 'Protein Swap', desc: 'More protein.', inputs: [{k:'food', l:'Original Food', p:'Oatmeal'}] },
    { id: 'fiber_rich_option', category: 'Nutrition', name: 'Fiber Boost', desc: 'Add more fiber.', inputs: [{k:'food', l:'Original Food', p:'White Bread'}] },
    { id: 'seasonal_swap', category: 'Nutrition', name: 'Seasonal Swap', desc: 'Eat seasonally.', inputs: [{k:'ingredient', l:'Ingredient', p:'Strawberries'}, {k:'season', l:'Current Season', p:'Winter', options: ['Spring', 'Summer', 'Autumn', 'Winter']}] },
    { id: 'budget_swap', category: 'Nutrition', name: 'Budget Saver', desc: 'Save money.', inputs: [{k:'ingredient', l:'Expensive Ingredient', p:'Pine Nuts'}] },
    { id: 'leftover_idea', category: 'Nutrition', name: 'Leftover Alchemist', desc: 'Use up leftovers.', inputs: [{k:'food', l:'Leftover Item', p:'Rotisserie Chicken'}] },
    { id: 'stress_relief', category: 'Wellness', name: 'Stress Relief', desc: 'Techniques to calm down.', inputs: [{k:'context', l:'Context', p:'Work Stress', options: ['Work Stress', 'Anxiety', 'Overwhelmed', 'Panic', 'Insomnia']}] },
    { id: 'focus_technique', category: 'Performance', name: 'Focus Mode', desc: 'Boost your concentration.', inputs: [{k:'task', l:'Task Type', p:'Deep Work', options: ['Deep Work', 'Studying', 'Creative Work', 'Admin Tasks', 'Reading']}] },
    { id: 'exercise_alternative', category: 'Performance', name: 'Exercise Swap', desc: 'Find an alternative exercise.', inputs: [{k:'exercise', l:'Exercise', p:'Running'}, {k:'reason', l:'Reason', p:'Knee Pain', options: ['Knee Pain', 'Back Pain', 'No Equipment', 'Boredom', 'Time Constraint']}] },
    { id: 'caffeine_optimizer', category: 'Wellness', name: 'Caffeine Optimizer', desc: 'Find your caffeine cutoff.', inputs: [{k:'sleep_time', l:'Bedtime', p:'10:00 PM'}, {k:'caffeine_amount', l:'Daily Intake (mg)', p:'200'}] },
    { id: 'fasting_timer', category: 'Nutrition', name: 'Fasting Timer', desc: 'Plan your next meal.', inputs: [{k:'last_meal_time', l:'Last Meal', p:'8:00 PM'}, {k:'fasting_type', l:'Fasting Type', p:'16:8', options: ['16:8', '18:6', '20:4', 'OMAD']}] },
    { id: 'circadian_sync', category: 'Wellness', name: 'Circadian Sync', desc: 'Optimize light exposure.', inputs: [{k:'wake_time', l:'Wake Up Time', p:'7:00 AM'}] },
    { id: 'macro_cheat_sheet', category: 'Nutrition', name: 'Macro Cheat Sheet', desc: 'Top sources for macros.', inputs: [{k:'macro_type', l:'Macro', p:'Protein', options: ['Protein', 'Carbs', 'Fats', 'Fiber']}, {k:'diet_preference', l:'Diet', p:'Omnivore', options: ['Omnivore', 'Vegan', 'Vegetarian', 'Keto', 'Paleo']}] },
    { id: 'breathwork_guide', category: 'Wellness', name: 'Breathwork Guide', desc: 'Guided breathing exercises.', inputs: [{k:'technique', l:'Technique', p:'Box Breathing', options: ['Box Breathing', '4-7-8 Relax', 'Wim Hof Style', 'Alternate Nostril']}] },
];

export const fitnessToolsList = [
     { id: 'calculate_1rm', name: '1 Rep Max Calc', desc: 'Estimate your max strength.', inputs: [{k:'weight', l:'Weight (kg/lbs)', p:'100'}, {k:'reps', l:'Reps', p:'5'}] },
     { id: 'heart_rate_zones', name: 'HR Zone Calc', desc: 'Find your training zones.', inputs: [{k:'age', l:'Age', p:'30'}, {k:'resting_hr', l:'Resting HR', p:'60'}] },
     { id: 'exercise_form_check', name: 'Form Check', desc: 'Key cues for safety.', inputs: [{k:'exercise', l:'Exercise', p:'Deadlift'}] },
];

export const lifestyleQuestions = [
    { id: 'gender', title: 'Biological Sex', desc: 'For metabolic calculation accuracy.', options: [{text:'Male', icon:'👨'}, {text:'Female', icon:'👩'}] },
    { id: 'age', title: 'Age Group', desc: 'Helps tailor nutritional needs.', options: [{text:'18-29', icon:'🎓'}, {text:'30-39', icon:'💼'}, {text:'40-49', icon:'🏡'}, {text:'50-59', icon:'👓'}, {text:'60+', icon:'👴'}] },
    { id: 'weight', title: 'Weight (approx)', desc: 'For BMI and Caloric needs.', options: [{text:'< 60kg', icon:'🪶'}, {text:'60-75kg', icon:'⚖️'}, {text:'75-90kg', icon:'🏋️'}, {text:'90-105kg', icon:'💪'}, {text:'105kg+', icon:'🦍'}] },
    { id: 'height', title: 'Height (approx)', desc: 'For BMI calculation.', options: [{text:'< 160cm', icon:'📏'}, {text:'160-170cm', icon:'📐'}, {text:'170-180cm', icon:'🧍'}, {text:'180-190cm', icon:'🏀'}, {text:'190cm+', icon:'🦒'}] },
    { id: 'activity', title: 'Activity Level', desc: 'Your daily energy expenditure?', options: [{text:'Sedentary (Desk Job)', icon:'🪑'}, {text:'Light (Walks)', icon:'🚶'}, {text:'Moderate (3-4x Gym)', icon:'🏃'}, {text:'Active (Daily Train)', icon:'🏋️'}, {text:'Athlete (2x Day)', icon:'🏅'}] },
    { id: 'goal', title: 'Primary Goal', desc: 'What are we aiming for?', options: [{text:'Weight Loss', icon:'📉'}, {text:'Muscle Gain', icon:'💪'}, {text:'Maintenance', icon:'⚖️'}, {text:'Endurance', icon:'🚴'}, {text:'Cognitive Performance', icon:'🧠'}, {text:'Stress Reduction', icon:'🧘'}, {text:'Gut Health', icon:'🦠'}] },
    { id: 'diet', title: 'Dietary Philosophy', desc: 'How do you prefer to eat?', options: [{text:'No Restrictions', icon:'🥩'}, {text:'Keto / Low Carb', icon:'🥑'}, {text:'Vegetarian', icon:'🥗'}, {text:'Vegan', icon:'🌱'}, {text:'Paleo', icon:'🍖'}, {text:'Carnivore', icon:'🥩'}, {text:'Pescatarian', icon:'🐟'}, {text:'Intermittent Fasting', icon:'⏳'}, {text:'Whole30', icon:'🍎'}, {text:'Low FODMAP', icon:'🌾'}, {text:'Flexitarian', icon:'🔄'}] },
    { id: 'allergies', title: 'Allergies / Exclusions', desc: 'Any absolute no-gos?', options: [{text:'None', icon:'✅'}, {text:'Gluten-Free', icon:'🍞'}, {text:'Dairy-Free', icon:'🥛'}, {text:'Nut-Free', icon:'🥜'}, {text:'Shellfish-Free', icon:'🦐'}, {text:'Soy-Free', icon:'🫘'}, {text:'Egg-Free', icon:'🥚'}, {text:'Fish-Free', icon:'🐟'}, {text:'Sesame-Free', icon:'🌭'}] },
    { id: 'cuisine', title: 'Flavor Palette', desc: 'What cuisines do you enjoy?', options: [{text:'Mediterranean', icon:'🫒'}, {text:'Asian / Stir-Fry', icon:'🥢'}, {text:'Mexican / Spicy', icon:'🌶️'}, {text:'Italian', icon:'🍝'}, {text:'Indian', icon:'🍛'}, {text:'Middle Eastern', icon:'🥙'}, {text:'American', icon:'🍔'}, {text:'French', icon:'🥐'}, {text:'Japanese', icon:'🍱'}, {text:'Thai', icon:'🍜'}, {text:'Greek', icon:'🏺'}] },
    { id: 'equipment', title: 'Workout Equipment', desc: 'What do you have access to?', options: [{text:'Full Commercial Gym', icon:'🏢'}, {text:'Home Gym (Basic)', icon:'🏠'}, {text:'Dumbbells Only', icon:'🏋️'}, {text:'Bodyweight Only', icon:'🧘'}, {text:'Resistance Bands', icon:'🎗️'}, {text:'Kettlebells', icon:'🔔'}, {text:'Cardio Machine', icon:'🏃'}] },
    { id: 'limitations', title: 'Physical Limitations', desc: 'Any injuries to work around?', options: [{text:'None', icon:'✨'}, {text:'Back Pain', icon:'🤕'}, {text:'Knee Issues', icon:'🦵'}, {text:'Shoulder Pain', icon:'🦾'}, {text:'Limited Mobility', icon:'🚶'}, {text:'Wrist Pain', icon:'👋'}, {text:'Ankle Issues', icon:'🦶'}] },
    { id: 'time', title: 'Cooking Time', desc: 'How much time for dinner?', options: [{text:'15 Mins (Quick)', icon:'⚡'}, {text:'30 Mins (Standard)', icon:'⏱️'}, {text:'45+ Mins (Chef)', icon:'👨‍🍳'}, {text:'Meal Prep (Batch)', icon:'📦'}] },
    { id: 'budget', title: 'Weekly Budget', desc: 'Target spending?', options: [{text:'Budget Friendly', icon:'💵'}, {text:'Moderate', icon:'💰'}, {text:'Premium (Organic)', icon:'💎'}] },
    { id: 'sleep', title: 'Sleep Quality', desc: 'How do you typically sleep?', options: [{text:'Good / Restful', icon:'😴'}, {text:'Insomnia / Trouble Falling', icon:'👀'}, {text:'Light Sleeper', icon:'🔊'}, {text:'Night Owl', icon:'🦉'}, {text:'Early Bird', icon:'🐔'}] },
    { id: 'stress', title: 'Stress Levels', desc: 'Current stress load?', options: [{text:'Low / Zen', icon:'🧘'}, {text:'Moderate', icon:'😐'}, {text:'High Pressure', icon:'🤯'}, {text:'Burnout', icon:'🔥'}] },
    { id: 'hydration', title: 'Hydration Habits', desc: 'Water intake?', options: [{text:'Consistent', icon:'💧'}, {text:'Needs Improvement', icon:'🥤'}, {text:'Dehydrated', icon:'🌵'}, {text:'Coffee Dependent', icon:'☕'}] },
    { id: 'meals', title: 'Meal Frequency', desc: 'How often do you eat?', options: [{text:'3 Main Meals', icon:'🍽️'}, {text:'Grazer / Snacker', icon:'🍿'}, {text:'Intermittent Fasting (16:8)', icon:'⏱️'}, {text:'OMAD (One Meal)', icon:'🛑'}] },
    { id: 'cooking_skill', title: 'Cooking Skill', desc: 'Kitchen confidence?', options: [{text:'Beginner', icon:'👶'}, {text:'Intermediate', icon:'🍳'}, {text:'Advanced / Pro', icon:'👨‍🍳'}, {text:'Microwave Only', icon:'📠'}] },
    { id: 'motivation', title: 'Primary Motivation', desc: 'What drives you?', options: [{text:'Look Good', icon:'💅'}, {text:'Feel Good / Energy', icon:'⚡'}, {text:'Longevity', icon:'🐢'}, {text:'Mental Clarity', icon:'🧠'}, {text:'Athletic Performance', icon:'🏅'}] }
];