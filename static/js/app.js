document.addEventListener('alpine:init', () => {
    Alpine.data('app', () => ({
        token: localStorage.getItem('bio_token') || Math.random().toString(36).substring(7),

        // State
        context: null,
        weekPlan: [],
        workoutPlan: [],
        chatHistory: [],
        toasts: [],

        // Loading States
        loading: false,
        loadingText: 'Initializing...',
        loadingInterval: null,

        // Consultation Mode (New)
        consultationActive: false,
        consultationStep: 0,
        currentIssue: null,
        userChoices: [],
        interviewQueue: [],    // <--- ADD THIS
        currentQuestion: null, // <--- ADD THIS
        userChoices: {},       // <--- ADD THIS
        bloodStrategies: [],   // <--- ADD THIS
        // Chat
        chatInput: '',
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
        quickPrompts: ['Does this meal plan have enough protein?', 'Can you swap Tuesday dinner?', 'I am feeling tired today.', 'Suggest a healthy snack.'],
        preferences: '',
        tempStrategy: null,

        // UX Features Data (Tooltips)
        tooltipVisible: false,
        tooltipText: '',
        tooltipX: 0,
        tooltipY: 0,
        tooltipTimeout: null,
        activeTooltipTerm: null,

        // Trackers
        waterIntake: 0,
        waterGoal: 8,
        fastingStart: null,
        fastingElapsed: '',
        fastingInterval: null,
        healthScore: 85,
        userName: 'Guest',

        // Bio Hacks Data
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

            document.addEventListener('mouseover', (e) => this.handleTooltipHover(e));
        },

        // --- UX LOGIC: SMART LOADING ---
        startLoading(phaseType) {
            this.loading = true;
            const thoughts = {
                'upload': ['Scanning PDF structure...', 'Extracting biomarkers...', 'Cross-referencing ranges...', 'Synthesizing health profile...'],
                'plan': ['Architecting Protocol...', 'Balancing Macros...', 'Optimizing Nutrient Density...', 'Finalizing Schedule...']
            };
            const phases = thoughts[phaseType] || thoughts['upload'];
            let i = 0;
            this.loadingText = phases[0];

            if(this.loadingInterval) clearInterval(this.loadingInterval);
            this.loadingInterval = setInterval(() => {
                i = (i + 1) % phases.length;
                this.loadingText = phases[i];
            }, 1800);
        },

        stopLoading() {
            this.loading = false;
            clearInterval(this.loadingInterval);
        },

        // --- CORE LOGIC: UPLOAD & CONSULTATION ---
        handleDrop(e) {
            this.dragOver = false;
            const file = e.dataTransfer.files[0];
            if (file) this.uploadData(file);
        },

        async uploadData(file) {
            if (!file) return;
            this.startLoading('upload');

            const fd = new FormData();
            fd.append('file', file);
            fd.append('token', this.token);

            try {
                const res = await fetch('/init_context', { method: 'POST', body: fd });
                if(!res.ok) throw new Error();
                this.context = await res.json();

                // Initialize Data
                this.healthScore = this.context.health_score || 78;
                this.userName = this.context.patient_name || 'Guest';

                // Start Consultation Mode if issues exist
                if (this.context.issues && this.context.issues.length > 0) {
                    this.startConsultation();
                } else {
                    // Fallback to Dashboard if no critical issues found
                    this.finalizeConsultation();
                }

                this.notify("Analysis Complete");
            } catch(e) {
                this.notify("Upload Failed", "error");
            } finally {
                this.stopLoading();
            }
        },

        // --- CONSULTATION MODE ---
        // --- ADVANCED CONSULTATION ENGINE ---

        // Configuration for the "Lifestyle" part of the interview
        lifestyleQuestions: [
            {
                id: 'diet',
                title: 'Dietary Philosophy',
                desc: 'How do you prefer to eat?',
                options: [
                    { text: 'No Restrictions', icon: '🥩' },
                    { text: 'Keto / Low Carb', icon: '🥑' },
                    { text: 'Vegetarian', icon: '🥗' },
                    { text: 'High Protein', icon: '💪' },
                    { text: 'Paleo', icon: '🍖' }
                ]
            },
            {
                id: 'cuisine',
                title: 'Flavor Palette',
                desc: 'What cuisines do you enjoy most?',
                options: [
                    { text: 'Mediterranean', icon: '🫒' },
                    { text: 'Asian / Stir-Fry', icon: '🥢' },
                    { text: 'Mexican / Spicy', icon: '🌶️' },
                    { text: 'Classic American', icon: '🍔' },
                    { text: 'Global Mix', icon: '🌎' }
                ]
            },
            {
                id: 'time',
                title: 'Time Commitment',
                desc: 'How much time do you have for dinner?',
                options: [
                    { text: '15 Mins (Quick)', icon: '⚡' },
                    { text: '30 Mins (Standard)', icon: '⏱️' },
                    { text: '45+ Mins (Chef Mode)', icon: '👨‍🍳' },
                    { text: 'Meal Prep / Bulk', icon: '📦' }
                ]
            },
            {
                id: 'budget',
                title: 'Weekly Budget',
                desc: 'How much do you want to spend?',
                options: [
                    { text: 'Budget Friendly', icon: '💵' },
                    { text: 'Moderate', icon: '💰' },
                    { text: 'Premium / Organic', icon: '💎' }
                ]
            }
        ],

        startConsultation() {
            this.consultationActive = true;
            this.consultationStep = 0;
            this.userChoices = {};     // Stores lifestyle answers
            this.bloodStrategies = []; // Stores choices for blood issues

            // Merge Blood Issues + Lifestyle Questions into one "Queue"
            // 1. Map Blood Issues to a standard format
            const bioQueue = (this.context.issues || []).map(issue => ({
                type: 'bio',
                title: `${issue.title} Detected`,
                desc: issue.explanation, // "Your Vitamin D is low..."
                value: issue.value,
                options: issue.options.map(opt => ({ text: opt.text, icon: opt.type === 'Diet' ? '🥦' : '🧘' }))
            }));

            // 2. Map Lifestyle Questions to standard format
            const lifeQueue = this.lifestyleQuestions.map(q => ({
                type: 'lifestyle',
                id: q.id,
                title: q.title,
                desc: q.desc,
                options: q.options
            }));

            // Combine them
            this.interviewQueue = [...bioQueue, ...lifeQueue];
            this.currentQuestion = this.interviewQueue[0];
        },

        selectOption(option) {
            // Save the answer based on the type of question
            if (this.currentQuestion.type === 'bio') {
                this.bloodStrategies.push(option.text);
            } else {
                this.userChoices[this.currentQuestion.id] = option.text;
            }

            // Next Step
            this.consultationStep++;

            if (this.consultationStep < this.interviewQueue.length) {
                this.currentQuestion = this.interviewQueue[this.consultationStep];
            } else {
                this.finalizeConsultation();
            }
        },

        async finalizeConsultation() {
            this.consultationActive = false;
            this.startLoading('plan'); // Start the "Architecting..." loading screen

            try {
                const [mealRes, workoutRes] = await Promise.all([
                    fetch('/generate_week', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        // SEND THE FULL PROFILE
                        body: JSON.stringify({
                            token: this.token,
                            blood_strategies: this.bloodStrategies,
                            lifestyle: this.userChoices
                        })
                    }),
                    fetch('/generate_workout', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            token: this.token,
                            strategy_name: this.userChoices.diet || "Balanced"
                        })
                    })
                ]);

                const data = await mealRes.json();
                const workoutData = await workoutRes.json();

                this.weekPlan = Array.isArray(data) ? data : [];
                this.workoutPlan = Array.isArray(workoutData) ? workoutData : [];

                this.currentTab = 'dashboard';
                this.notify("Protocol Optimized & Active");
            } catch(e) {
                this.notify("Generation Failed", "error");
            } finally {
                this.stopLoading();
            }
        },

        async generateWeek() {
            this.prefModalOpen = false;
            this.startLoading('plan');

            try {
                const [mealRes, workoutRes] = await Promise.all([
                    fetch('/generate_week', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ strategy_name: this.tempStrategy, token: this.token, preferences: this.preferences })
                    }),
                    fetch('/generate_workout', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ strategy_name: this.tempStrategy, token: this.token })
                    })
                ]);

                const data = await mealRes.json();
                const workoutData = await workoutRes.json();

                this.weekPlan = Array.isArray(data) ? data : [];
                this.workoutPlan = Array.isArray(workoutData) ? workoutData : [];

                this.currentTab = 'dashboard';
                this.notify("Protocol Active");
            } catch(e) {
                this.notify("Generation Failed", "error");
            } finally {
                this.stopLoading();
            }
        },

        // --- CHAT LOGIC ---
        async sendMessage() {
            if(!this.chatInput.trim()) return;
            const msg = this.chatInput;

            this.chatHistory.push({ role: 'user', text: msg });
            this.chatInput = '';
            this.scrollToBottom();

            this.chatLoading = true;
            const aiIndex = this.chatHistory.push({ role: 'ai', text: '', typing: true }) - 1;

            try {
                const res = await fetch('/chat_agent', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ message: msg, token: this.token })
                });
                const data = await res.json();

                this.chatLoading = false;
                await this.typeWriterEffect(aiIndex, data.response);

            } catch(e) {
                this.chatHistory[aiIndex].text = "Connection interrupted.";
                this.chatHistory[aiIndex].typing = false;
            } finally {
                this.chatLoading = false;
            }
        },

        typeWriterEffect(index, fullText) {
            return new Promise(resolve => {
                if(!fullText) {
                    this.chatHistory[index].text = "I couldn't process that.";
                    this.chatHistory[index].typing = false;
                    resolve(); return;
                }
                let i = 0;
                const speed = 15;
                const type = () => {
                    if (i < fullText.length) {
                        this.chatHistory[index].text += fullText.charAt(i);
                        i++;
                        this.scrollToBottom();
                        setTimeout(type, speed);
                    } else {
                        this.chatHistory[index].typing = false;
                        resolve();
                    }
                };
                type();
            });
        },

        scrollToBottom() {
            this.$nextTick(() => {
                const container = document.getElementById('chat-container');
                if(container) container.scrollTop = container.scrollHeight;
            });
        },

        // --- UX LOGIC: TOOLTIPS ---
        handleTooltipHover(e) {
            const target = e.target.closest('[data-term]');
            if (!target) {
                this.tooltipVisible = false;
                this.activeTooltipTerm = null;
                return;
            }

            const term = target.getAttribute('data-term');
            if (this.activeTooltipTerm === term) {
                this.moveTooltip(e);
                this.tooltipVisible = true;
                return;
            }

            this.activeTooltipTerm = term;
            this.tooltipText = "Analyzing...";
            this.tooltipVisible = true;
            this.moveTooltip(e);

            if (this.tooltipTimeout) clearTimeout(this.tooltipTimeout);

            this.tooltipTimeout = setTimeout(async () => {
                try {
                    const res = await fetch('/define_term', {
                        method: 'POST', headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ term: term })
                    });
                    const data = await res.json();
                    if(this.activeTooltipTerm === term) {
                        this.tooltipText = data.response || data.definition || "No definition found.";
                    }
                } catch(err) {
                    this.tooltipText = "Could not load definition.";
                }
            }, 300);
        },

        moveTooltip(e) {
            let x = e.clientX + 15;
            let y = e.clientY + 15;
            if (x > window.innerWidth - 260) x = e.clientX - 260;
            if (y > window.innerHeight - 100) y = e.clientY - 100;
            this.tooltipX = x;
            this.tooltipY = y;
        },

        // --- UTILITIES ---
        saveSettings() {
            localStorage.setItem('userName', this.userName);
            this.notify("Settings Saved");
        },

        notify(msg, type='success') {
            const id = Date.now();
            this.toasts.push({ id, message: msg, type });
            setTimeout(() => {
                this.toasts = this.toasts.filter(t => t.id !== id);
            }, 3000);
        },

        openPrefModal(strategy) {
            this.tempStrategy = strategy;
            this.prefModalOpen = true;
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
            if(confirm('Reset all data and start over?')) {
                this.context = null;
                this.weekPlan = [];
                this.chatHistory = [];
                this.toasts = [];
                this.currentTab = 'dashboard';
                localStorage.clear();
                window.location.reload();
            }
        },

        // --- BIOHACKS & TRACKERS ---
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
            if(data.response) return data.response;
            if(data.definition) return data.definition;

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