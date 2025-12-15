export function nutritionSlice() {
    return {
        // --- NUTRITION STATE ---
        weekPlan: [],
        mealWizardOpen: false,
        mealStrategies: [],
        selectedStrategy: null,
        recipeModalOpen: false,
        shoppingListOpen: false,
        customMealModalOpen: false,
        selectedMeal: null,
        customMealDate: null,
        customMealForm: { title: '', calories: '', protein: '', carbs: '', fats: '', type: 'Snack' },
        recipeDetails: null,
        shoppingList: null,
        nutritionToolIds: ['quick_snack', 'check_food_interaction', 'recipe_variation', 'seasonal_swap', 'budget_swap', 'leftover_idea', 'flavor_pairing', 'mood_food', 'low_gi_option', 'high_protein_option'],
        mealNotesModalOpen: false,
        mealNoteInput: '',
        currentMealForNotes: null,

        // --- NUTRITION METHODS ---
        getMacroValue(str) {
            return parseInt(String(str).replace(/\D/g, '')) || 0;
        },

        getMacroPercent(valStr, target) {
            const val = this.getMacroValue(valStr);
            return Math.min(100, Math.round((val / target) * 100));
        },

        openMealNotes(meal) {
            this.currentMealForNotes = meal;
            this.mealNoteInput = meal.notes || '';
            this.mealNotesModalOpen = true;
        },

        saveMealNotes() {
            if(this.currentMealForNotes) {
                this.currentMealForNotes.notes = this.mealNoteInput;
                this.notify("Note Saved 📝");
                this.mealNotesModalOpen = false;
            }
        },

        getMealsForSelectedDate() {
            if(!this.weekPlan.length) return [];

            // FIXED: Match by Date String, not Array Index
            const foundPlan = this.weekPlan.find(day => day.date === this.selectedDate);
            return foundPlan ? [foundPlan] : [];
        },

        toggleMealCompletion(meal) {
            meal.completed = !meal.completed;
            if(meal.completed) {
                this.notify("Meal Logged! Stats Updated.");
                this.logActivity(`Ate ${meal.title}`, '🍽️');
            }
        },

        getNutritionTools() {
            return this.tools.filter(t => this.nutritionToolIds.includes(t.id));
        },

        getToolIcon(toolId) {
            const icons = {
                'quick_snack': '🍎',
                'check_food_interaction': '⚠️',
                'recipe_variation': '🍲',
                'seasonal_swap': '🍂',
                'budget_swap': '💰',
                'leftover_idea': '🥡',
                'flavor_pairing': '👩‍🍳',
                'mood_food': '🎭',
                'low_gi_option': '📉',
                'high_protein_option': '💪'
            };
            return icons[toolId] || '✨';
        },

        getMealIcon(type) {
            const t = (type || '').toLowerCase();
            if(t.includes('breakfast')) return '🍳';
            if(t.includes('lunch')) return '🥗';
            if(t.includes('dinner')) return '🍽️';
            if(t.includes('snack')) return '🥜';
            if(t.includes('pre')) return '⚡';
            if(t.includes('post')) return '🥛';
            return '🍴';
        },

        openAddMealModal(day) {
            this.customMealDate = day;
            this.customMealForm = { title: '', calories: '', protein: '', carbs: '', fats: '', type: 'Snack' };
            this.customMealModalOpen = true;
        },

        addCustomMeal() {
             const dateStr = this.customMealDate.date || this.customMealDate.fullDate;

             // FIXED: Find day by matching date string
             const dayPlan = this.weekPlan.find(d => d.date === dateStr);

             if (!dayPlan) {
                 this.notify("No plan exists for this date.", "error");
                 return;
             }

             const meal = {
                 ...this.customMealForm,
                 completed: false,
                 benefit: 'Custom Entry'
             };

             dayPlan.meals.push(meal);

             // Update totals
             const currentTotals = dayPlan.total_macros;
             const parseVal = (str) => parseInt(String(str).replace(/\D/g, '')) || 0;

             currentTotals.calories = parseVal(currentTotals.calories) + parseVal(meal.calories);
             currentTotals.protein = (parseVal(currentTotals.protein) + parseVal(meal.protein)) + 'g';
             currentTotals.carbs = (parseVal(currentTotals.carbs) + parseVal(meal.carbs)) + 'g';
             currentTotals.fats = (parseVal(currentTotals.fats) + parseVal(meal.fats)) + 'g';

             this.customMealModalOpen = false;
             this.notify("Meal Added");

             // Force Chart Refresh
             this.initNutritionCharts();
        },

        async openRecipe(meal) {
            this.selectedMeal = meal; this.recipeDetails = null; this.recipeModalOpen = true;
            try {
                const res = await fetch('/get_recipe', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ meal_title: meal.title, token: this.token }) });
                this.recipeDetails = await res.json();
            } catch(e) {}
        },

        async generateShoppingList() {
            this.shoppingListOpen = true; if(this.shoppingList) return;
            try {
                const res = await fetch('/generate_shopping_list', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ token: this.token }) });
                this.shoppingList = await res.json();
            } catch(e) {}
        },

        downloadList() {
            if (!this.shoppingList) return;
            let text = "BIOFLOW SHOPPING LIST\n=====================\n\n";
            for (const [cat, items] of Object.entries(this.shoppingList)) { text += `[ ${cat.toUpperCase()} ]\n`; items.forEach(i => text += ` - ${i}\n`); text += "\n"; }
            const blob = new Blob([text], { type: 'text/plain' });
            const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = 'shopping-list.txt'; a.click();
        },

        async quickSwap(day, ing) {
            this.chatOpen = true; this.chatInput = `I can't eat ${ing} in the ${day.title}. Alternative?`; this.sendMessage();
        },

        // --- CORE GENERATION LOGIC ---
        async openMealWizard() {
            this.mealWizardOpen = true;
            this.mealStrategies = [];
            this.startLoading(['Analyzing Metabolism...', 'Drafting Strategies...']);

            try {
                const res = await fetch('/propose_meal_strategies', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ token: this.token })
                });
                this.mealStrategies = await res.json();
            } catch(e) {
                this.notify("AI Brain Offline", "error");
                this.mealWizardOpen = false;
            } finally {
                this.stopLoading();
            }
        },

        async selectMealStrategy(strat) {
            this.mealWizardOpen = false;
            this.startLoading(['Architecting Full Week...', 'Calibrating Macros...']);
            await this.executePlanGeneration(strat.title);
        },

        async executePlanGeneration(strategyName) {
            try {
                const [mealRes, workoutRes] = await Promise.all([
                    fetch('/generate_week', {
                        method: 'POST', headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            token: this.token,
                            strategy_name: strategyName,
                            blood_strategies: this.bloodStrategies,
                            lifestyle: this.userChoices
                        })
                    }),
                    fetch('/generate_workout', {
                        method: 'POST', headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            token: this.token,
                            strategy_name: strategyName,
                            fitness_strategy: this.selectedFitnessStrategy?.title || strategyName,
                            lifestyle: this.userChoices
                        })
                    })
                ]);

                const data = await mealRes.json();
                const workoutData = await workoutRes.json();

                // Assign valid dates to the week plan starting from TODAY
                this.weekPlan = data.map((daily, index) => {
                    const targetDate = new Date();
                    targetDate.setDate(new Date().getDate() + index); // Today + index
                    const dateStr = targetDate.toISOString().split('T')[0];

                    const meals = daily.meals ? daily.meals.map(m => ({...m, completed: false})) : [];

                    return {
                        ...daily,
                        meals: meals,
                        date: dateStr,
                        completed: false
                    };
                });

                // Assign valid dates to the workout plan starting from TODAY
                this.workoutPlan = workoutData.map((daily, index) => {
                    const targetDate = new Date();
                    targetDate.setDate(new Date().getDate() + index); // Today + index
                    const dateStr = targetDate.toISOString().split('T')[0];

                    // Map specific day names if needed (e.g. AI returns "Day 1", we want "Mon")
                    const dayName = targetDate.toLocaleDateString('en-US', { weekday: 'short' });

                    return {
                        ...daily,
                        day: dayName, // Overwrite AI's "Day 1" with "Mon"
                        date: dateStr,
                        exercises: daily.exercises ? daily.exercises.map(ex => {
                            const exObj = (typeof ex === 'string') ? { name: ex } : ex;
                            return {
                                ...exObj,
                                completed: false,
                                weight: '',
                                performedReps: '',
                                notes: ''
                            };
                        }) : []
                    };
                });

                localStorage.setItem('weekPlan', JSON.stringify(this.weekPlan));
                localStorage.setItem('workoutPlan', JSON.stringify(this.workoutPlan));

                this.currentTab = 'dashboard';
                this.notify("Protocol Optimized");

                // Refresh Charts
                setTimeout(() => {
                    if (this.initDashboardCharts) this.initDashboardCharts();
                    if (this.initNutritionCharts) this.initNutritionCharts();
                }, 500);

            } catch(e) {
                console.error(e);
                this.notify("Generation Failed", "error");
            } finally {
                this.stopLoading();
            }
        }
    }
}