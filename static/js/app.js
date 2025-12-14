document.addEventListener('alpine:init', () => {
    Alpine.data('app', () => ({
        token: localStorage.getItem('bio_token') || Math.random().toString(36).substring(7),
        context: null,
        weekPlan: [],
        workoutPlan: [],
        chatHistory: [],
        toasts: [],
        loading: false,
        chatLoading: false,
        chatOpen: false,

        // Navigation
        currentTab: 'dashboard',

        // Modals
        recipeModalOpen: false,
        shoppingListOpen: false,
        workoutModalOpen: false,
        prefModalOpen: false,
        bioHacksOpen: false,
        dragOver: false,

        // Data
        selectedMeal: null,
        recipeDetails: null,
        shoppingList: null,
        chatInput: '',
        quickPrompts: ['Does this meal plan have enough protein?', 'Can you swap Tuesday dinner?', 'I am feeling tired today.', 'Suggest a healthy snack.'],
        loadingText: 'Initializing...',
        loadingInterval: null,
        preferences: '',
        tempStrategy: null,

        // New Features Data
        waterIntake: 0,
        waterGoal: 8,
        fastingStart: null,
        fastingElapsed: '',
        fastingInterval: null,
        healthScore: 85,
        userName: 'Guest',

        // Bio Hacks
        selectedTool: null,
        toolInputs: {},
        toolResult: null,
        toolLoading: false,
        tools: [
            { id: 'suggest_supplement', name: 'Supplement Advisor', desc: 'Get supplement recommendations.', inputs: [{k:'focus', l:'Focus', p:'Joint Health', options: ['Joint Health', 'Energy', 'Sleep', 'Immunity', 'Stress', 'Digestion']}] },
            { id: 'check_food_interaction', name: 'Interaction Checker', desc: 'Check if foods clash.', inputs: [{k:'item1', l:'Item A', p:'Grapefruit'}, {k:'item2', l:'Item B', p:'Medication'}] },
            { id: 'recipe_variation', name: 'Recipe Variator', desc: 'Modify a recipe.', inputs: [{k:'recipe', l:'Original Recipe', p:'Lasagna'}, {k:'type', l:'Variation Type', p:'Keto', options: ['Keto', 'Vegan', 'Paleo', 'Low-Carb', 'Gluten-Free']}] },
            { id: 'flavor_pairing', name: 'Flavor Pairer', desc: 'Find matching flavors.', inputs: [{k:'ingredient', l:'Ingredient', p:'Salmon'}] },
            { id: 'quick_snack', name: 'Snack Generator', desc: 'Get a quick snack idea.', inputs: [{k:'preference', l:'Preference', p:'Savory', options: ['Savory', 'Sweet', 'Crunchy', 'High Protein', 'Low Calorie']}] },
            { id: 'hydration_tip', name: 'Hydration Coach', desc: 'Tips for hydration.', inputs: [{k:'activity', l:'Activity Level', p:'High Intensity', options: ['Sedentary', 'Light Activity', 'Moderate Activity', 'High Intensity', 'Athlete']}] },
            { id: 'mood_food', name: 'Mood Food', desc: 'Food for your mood.', inputs: [{k:'mood', l:'Current Mood', p:'Stressed', options: ['Stressed', 'Happy', 'Sad', 'Anxious', 'Tired', 'Energetic']}] },
            { id: 'energy_booster', name: 'Energy Booster', desc: 'Natural energy sources.', inputs: [{k:'context', l:'Context', p:'Afternoon Slump', options: ['Morning', 'Afternoon Slump', 'Pre-Workout', 'Late Night']}] },
            { id: 'recovery_meal', name: 'Recovery Meal', desc: 'Post-workout fuel.', inputs: [{k:'workout', l:'Workout Type', p:'Heavy Lifting', options: ['Heavy Lifting', 'Cardio', 'HIIT', 'Yoga', 'Sports']}] },
            { id: 'sleep_aid', name: 'Sleep Aid', desc: 'Foods to help sleep.', inputs: [{k:'issue', l:'Sleep Issue', p:'Trouble Falling Asleep', options: ['Trouble Falling Asleep', 'Waking Up Frequently', 'Light Sleeper', 'Insomnia']}] },
            { id: 'digestive_aid', name: 'Digestive Helper', desc: 'Foods for digestion.', inputs: [{k:'symptom', l:'Symptom', p:'Bloating', options: ['Bloating', 'Indigestion', 'Nausea', 'Heartburn', 'Constipation']}] },
            { id: 'immunity_booster', name: 'Immunity Boost', desc: 'Boost your immune system.', inputs: [{k:'season', l:'Season/Context', p:'Flu Season', options: ['Flu Season', 'Winter', 'Spring', 'Traveling', 'Stressful Period']}] },
            { id: 'anti_inflammatory', name: 'Inflammation Fighter', desc: 'Reduce inflammation.', inputs: [{k:'condition', l:'Concern', p:'General', options: ['General', 'Joint Pain', 'Gut Health', 'Skin Issues', 'Headaches']}] },
            { id: 'antioxidant_rich', name: 'Antioxidant Finder', desc: 'Find rich foods.', inputs: [{k:'preference', l:'Preference', p:'Berries', options: ['Berries', 'Vegetables', 'Nuts', 'Teas', 'Spices']}] },
            { id: 'low_gi_option', name: 'Low GI Swap', desc: 'Stable blood sugar.', inputs: [{k:'food', l:'High GI Food', p:'White Rice'}] },
            { id: 'high_protein_option', name: 'Protein Swap', desc: 'More protein.', inputs: [{k:'food', l:'Original Food', p:'Oatmeal'}] },
            { id: 'fiber_rich_option', name: 'Fiber Boost', desc: 'Add more fiber.', inputs: [{k:'food', l:'Original Food', p:'White Bread'}] },
            { id: 'seasonal_swap', name: 'Seasonal Swap', desc: 'Eat seasonally.', inputs: [{k:'ingredient', l:'Ingredient', p:'Strawberries'}, {k:'season', l:'Current Season', p:'Winter', options: ['Spring', 'Summer', 'Autumn', 'Winter']}] },
            { id: 'budget_swap', name: 'Budget Saver', desc: 'Save money.', inputs: [{k:'ingredient', l:'Expensive Ingredient', p:'Pine Nuts'}] },
            { id: 'leftover_idea', name: 'Leftover Alchemist', desc: 'Use up leftovers.', inputs: [{k:'food', l:'Leftover Item', p:'Rotisserie Chicken'}] },
            { id: 'stress_relief', name: 'Stress Relief', desc: 'Techniques to calm down.', inputs: [{k:'context', l:'Context', p:'Work Stress', options: ['Work Stress', 'Anxiety', 'Overwhelmed', 'Panic', 'Insomnia']}] },
            { id: 'focus_technique', name: 'Focus Mode', desc: 'Boost your concentration.', inputs: [{k:'task', l:'Task Type', p:'Deep Work', options: ['Deep Work', 'Studying', 'Creative Work', 'Admin Tasks', 'Reading']}] },
            { id: 'exercise_alternative', name: 'Exercise Swap', desc: 'Find an alternative exercise.', inputs: [{k:'exercise', l:'Exercise', p:'Running'}, {k:'reason', l:'Reason', p:'Knee Pain', options: ['Knee Pain', 'Back Pain', 'No Equipment', 'Boredom', 'Time Constraint']}] },
        ],

        init() {
            localStorage.setItem('bio_token', this.token);
            const savedWater = localStorage.getItem('waterIntake');
            if (savedWater) this.waterIntake = parseInt(savedWater);

            const savedFasting = localStorage.getItem('fastingStart');
            if (savedFasting) {
                this.fastingStart = parseInt(savedFasting);
                this.startFastingTimer();
            }

            const savedName = localStorage.getItem('userName');
            if(savedName) this.userName = savedName;
        },

        saveSettings() {
            localStorage.setItem('userName', this.userName);
            this.notify("Settings Saved");
        },

        notify(msg, type='success') {
            const id = Date.now();
            this.toasts = [];
            this.$nextTick(() => {
                this.toasts.push({ id, message: msg, type });
            });
            setTimeout(() => { this.toasts = [] }, 4000);
        },

        startLoading(phases) {
            this.loading = true;
            let i = 0;
            this.loadingText = phases[0];
            this.loadingInterval = setInterval(() => {
                i = (i + 1) % phases.length;
                this.loadingText = phases[i];
            }, 1500);
        },

        stopLoading() {
            this.loading = false;
            clearInterval(this.loadingInterval);
        },

        handleDrop(e) {
            this.dragOver = false;
            const file = e.dataTransfer.files[0];
            if (file) this.uploadData(file);
        },

        async uploadData(file) {
            if (!file) return;
            this.startLoading(['Analyzing Biomarkers...', 'Synthesizing Data...', 'Reviewing Hormonal Profile...']);

            const fd = new FormData();
            fd.append('file', file);
            fd.append('token', this.token);

            try {
                const res = await fetch('/init_context', { method: 'POST', body: fd });
                if(!res.ok) throw new Error();
                this.context = await res.json();
                this.notify("Analysis Complete");
            } catch(e) {
                this.notify("Upload Failed", "error");
            } finally {
                this.stopLoading();
            }
        },

        openPrefModal(strategy) {
            this.tempStrategy = strategy;
            this.prefModalOpen = true;
        },

        async generateWeek() {
            this.prefModalOpen = false;
            const strategy = this.tempStrategy;
            this.startLoading(['Architecting Protocol...', 'Balancing Macros...', 'Designing Workouts...', 'Finalizing Plan...']);
            try {
                const [mealRes, workoutRes] = await Promise.all([
                    fetch('/generate_week', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ strategy_name: strategy, token: this.token, preferences: this.preferences })
                    }),
                    fetch('/generate_workout', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ strategy_name: strategy, token: this.token })
                    })
                ]);

                const data = await mealRes.json();
                const workoutData = await workoutRes.json();

                this.weekPlan = Array.isArray(data) ? data : [];
                this.workoutPlan = Array.isArray(workoutData) ? workoutData : [];

                this.currentTab = 'dashboard';
                this.healthScore = Math.floor(Math.random() * (98 - 75) + 75);

                this.notify("Full Protocol Active");
            } catch(e) {
                this.notify("Generation Failed", "error");
            } finally {
                this.stopLoading();
            }
        },

        async sendMessage() {
            if(!this.chatInput.trim()) return;
            const msg = this.chatInput;
            this.chatHistory.push({ role: 'user', text: msg });
            this.chatInput = '';
            this.chatLoading = true;
            this.scrollToBottom();

            try {
                const res = await fetch('/chat_agent', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ message: msg, token: this.token })
                });
                const data = await res.json();
                this.chatHistory.push({ role: 'ai', text: data.response });
            } catch(e) {
                this.chatHistory.push({ role: 'ai', text: "Connection interrupted." });
            } finally {
                this.chatLoading = false;
                this.scrollToBottom();
            }
        },

        scrollToBottom() {
            this.$nextTick(() => {
                const container = document.getElementById('chat-container');
                if(container) container.scrollTop = container.scrollHeight;
            });
        },

        async openRecipe(meal) {
            this.selectedMeal = meal;
            this.recipeDetails = null;
            this.recipeModalOpen = true;
            try {
                const res = await fetch('/get_recipe', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ meal_title: meal.title, token: this.token })
                });
                this.recipeDetails = await res.json();
            } catch(e) { this.notify("Could not fetch recipe", "error"); }
        },

        async generateShoppingList() {
            this.shoppingListOpen = true;
            if(this.shoppingList) return;
            try {
                const res = await fetch('/generate_shopping_list', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ token: this.token })
                });
                this.shoppingList = await res.json();
            } catch(e) {}
        },

        downloadList() {
            if (!this.shoppingList) return;
            let text = "BIOFLOW SHOPPING LIST\n=====================\n\n";
            for (const [cat, items] of Object.entries(this.shoppingList)) {
                text += `[ ${cat.toUpperCase()} ]\n`;
                items.forEach(i => text += ` - ${i}\n`);
                text += "\n";
            }
            const blob = new Blob([text], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'shopping-list.txt';
            a.click();
        },

        async quickSwap(day, ing) {
            this.chatOpen = true;
            this.chatInput = `I can't eat ${ing} in the ${day.title}. What's a good alternative?`;
            this.sendMessage();
        },

        resetSystem() {
            if(confirm('Start a new session?')) {
                this.context = null;
                this.weekPlan = [];
                this.chatHistory = [];
                this.toasts = [];
                this.currentTab = 'dashboard';
                localStorage.clear();
                window.location.reload();
            }
        },

        closeBioHacks() {
            this.bioHacksOpen = false;
        },

        selectTool(tool) {
            this.selectedTool = tool;
            this.toolInputs = {};
            this.toolResult = null;
        },

        async runTool() {
            if(!this.selectedTool) return;
            this.toolLoading = true;
            this.toolResult = null;
            try {
                const res = await fetch(`/${this.selectedTool.id}`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(this.toolInputs)
                });
                const data = await res.json();
                this.toolResult = this.formatResult(data);
            } catch(e) {
                this.toolResult = "Error connecting to Bio-Architect.";
            } finally {
                this.toolLoading = false;
            }
        },

        formatResult(data) {
            if(!data) return "No data returned.";
            if(data.supplements) return data.supplements.map(s => `• ${s.name}: ${s.reason}`).join('\n');
            if(data.foods) return data.foods.map(f => `• ${f}`).join('\n');
            if(data.interaction) return `Status: ${data.interaction}\n${data.details}`;
            if(data.recipe) return `Recipe: ${data.recipe}\n${data.changes || ''}`;
            if(data.pairings) return data.pairings.map(p => `• ${p}`).join('\n');

            let output = "";
            for(const [key, val] of Object.entries(data)) {
                const label = key.replace(/_/g, ' ').toUpperCase();
                output += `${label}: ${val}\n`;
            }
            return output;
        },

        addWater() {
            if(this.waterIntake < this.waterGoal) {
                this.waterIntake++;
                localStorage.setItem('waterIntake', this.waterIntake);
                if(this.waterIntake === this.waterGoal) this.notify("Hydration Goal Met! 💧");
            }
        },
        resetWater() {
            this.waterIntake = 0;
            localStorage.setItem('waterIntake', 0);
        },

        toggleFasting() {
            if (this.fastingStart) {
                this.fastingStart = null;
                localStorage.removeItem('fastingStart');
                clearInterval(this.fastingInterval);
                this.fastingElapsed = '';
                this.notify("Fasting Ended");
            } else {
                this.fastingStart = Date.now();
                localStorage.setItem('fastingStart', this.fastingStart);
                this.startFastingTimer();
                this.notify("Fasting Started ⏳");
            }
        },

        startFastingTimer() {
            this.updateFastingTimer();
            this.fastingInterval = setInterval(() => {
                this.updateFastingTimer();
            }, 1000 * 60);
        },

        updateFastingTimer() {
            if (!this.fastingStart) return;
            const diff = Date.now() - this.fastingStart;
            const hours = Math.floor(diff / (1000 * 60 * 60));
            const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            this.fastingElapsed = `${hours}h ${minutes}m`;
        }
    }))
});
