document.addEventListener('alpine:init', () => {
    Alpine.data('app', () => ({
        // --- 1. AUTH & CONFIG ---
        token: localStorage.getItem('bio_token') || Math.random().toString(36).substring(7),

        // --- 2. GLOBAL STATE ---
        context: null,
        weekPlan: [],
        workoutPlan: [],
        chatHistory: [],
        toasts: [],

        // --- 3. LOADING STATE ---
        loading: false,
        loadingText: 'Initializing...',
        loadingInterval: null,

        // --- 4. CHAT STATE ---
        chatInput: '',
        chatLoading: false,
        chatOpen: false,  // <--- This was missing/unreachable causing the error

        // --- 5. NAVIGATION ---
        currentTab: 'dashboard',

        // --- 6. MODALS ---
        recipeModalOpen: false,
        shoppingListOpen: false,
        workoutModalOpen: false,
        prefModalOpen: false,
        bioHacksOpen: false,
        dragOver: false,

        // --- 7. DATA OBJECTS ---
        bloodMarkers: [],
        selectedMeal: null,
        recipeDetails: null,
        shoppingList: null,
        quickPrompts: ['Does this meal plan have enough protein?', 'Can you swap Tuesday dinner?', 'I am feeling tired today.', 'Suggest a healthy snack.'],
        preferences: '',
        tempStrategy: null,

        // --- 8. CALENDAR STATE ---
        calendarDays: [],
        selectedDate: null,
        mealWizardOpen: false,
        mealStrategies: [],
        selectedStrategy: null,

        // --- 9. CONSULTATION STATE ---
        consultationActive: false,
        consultationStep: 0,
        interviewQueue: [],
        currentQuestion: null,
        userChoices: {},
        bloodStrategies: [],

        // --- 10. TOOLTIP STATE ---
        tooltipVisible: false,
        tooltipText: '',
        tooltipX: 0,
        tooltipY: 0,
        tooltipTimeout: null,
        activeTooltipTerm: null,

        // --- 11. TRACKERS ---
        waterIntake: 0,
        waterGoal: 8,
        fastingStart: null,
        fastingElapsed: '',
        fastingInterval: null,
        healthScore: 85,
        userName: 'Guest',

        // --- 12. BIO HACKS TOOLS ---
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

        // --- 13. LIFESTYLE QUESTIONS ---
        lifestyleQuestions: [
            // Basics
            { id: 'gender', title: 'Biological Sex', desc: 'For metabolic calculation accuracy.', options: [{text:'Male', icon:'👨'}, {text:'Female', icon:'👩'}] },
            { id: 'age', title: 'Age Group', desc: 'Helps tailor nutritional needs.', options: [{text:'18-29', icon:'🎓'}, {text:'30-39', icon:'💼'}, {text:'40-49', icon:'🏡'}, {text:'50-59', icon:'👓'}, {text:'60+', icon:'👴'}] },

            // Fitness & Health
            { id: 'activity', title: 'Activity Level', desc: 'Your daily energy expenditure?', options: [{text:'Sedentary (Desk Job)', icon:'🪑'}, {text:'Light (Walks)', icon:'🚶'}, {text:'Moderate (3-4x Gym)', icon:'🏃'}, {text:'Active (Daily Train)', icon:'🏋️'}, {text:'Athlete (2x Day)', icon:'🏅'}] },
            { id: 'goal', title: 'Primary Goal', desc: 'What are we aiming for?', options: [{text:'Weight Loss', icon:'📉'}, {text:'Muscle Gain', icon:'💪'}, {text:'Maintenance', icon:'⚖️'}, {text:'Endurance', icon:'🚴'}, {text:'Cognitive Performance', icon:'🧠'}, {text:'Stress Reduction', icon:'🧘'}, {text:'Gut Health', icon:'🦠'}] },

            // Nutrition Deep Dive
            { id: 'diet', title: 'Dietary Philosophy', desc: 'How do you prefer to eat?', options: [{text:'No Restrictions', icon:'🥩'}, {text:'Keto / Low Carb', icon:'🥑'}, {text:'Vegetarian', icon:'🥗'}, {text:'Vegan', icon:'🌱'}, {text:'Paleo', icon:'🍖'}, {text:'Carnivore', icon:'🥩'}, {text:'Pescatarian', icon:'🐟'}, {text:'Intermittent Fasting', icon:'⏳'}, {text:'Whole30', icon:'🍎'}, {text:'Low FODMAP', icon:'🌾'}, {text:'Flexitarian', icon:'🔄'}] },
            { id: 'allergies', title: 'Allergies / Exclusions', desc: 'Any absolute no-gos?', options: [{text:'None', icon:'✅'}, {text:'Gluten-Free', icon:'🍞'}, {text:'Dairy-Free', icon:'🥛'}, {text:'Nut-Free', icon:'🥜'}, {text:'Shellfish-Free', icon:'🦐'}, {text:'Soy-Free', icon:'🫘'}, {text:'Egg-Free', icon:'🥚'}, {text:'Fish-Free', icon:'🐟'}, {text:'Sesame-Free', icon:'🌭'}] },
            { id: 'cuisine', title: 'Flavor Palette', desc: 'What cuisines do you enjoy?', options: [{text:'Mediterranean', icon:'🫒'}, {text:'Asian / Stir-Fry', icon:'🥢'}, {text:'Mexican / Spicy', icon:'🌶️'}, {text:'Italian', icon:'🍝'}, {text:'Indian', icon:'🍛'}, {text:'Middle Eastern', icon:'🥙'}, {text:'American', icon:'🍔'}, {text:'French', icon:'🥐'}, {text:'Japanese', icon:'🍱'}, {text:'Thai', icon:'🍜'}, {text:'Greek', icon:'🏺'}] },

            // Logistics
            { id: 'equipment', title: 'Workout Equipment', desc: 'What do you have access to?', options: [{text:'Full Commercial Gym', icon:'🏢'}, {text:'Home Gym (Basic)', icon:'🏠'}, {text:'Dumbbells Only', icon:'🏋️'}, {text:'Bodyweight Only', icon:'🧘'}, {text:'Resistance Bands', icon:'🎗️'}, {text:'Kettlebells', icon:'🔔'}, {text:'Cardio Machine', icon:'🏃'}] },
            { id: 'limitations', title: 'Physical Limitations', desc: 'Any injuries to work around?', options: [{text:'None', icon:'✨'}, {text:'Back Pain', icon:'🤕'}, {text:'Knee Issues', icon:'🦵'}, {text:'Shoulder Pain', icon:'🦾'}, {text:'Limited Mobility', icon:'🚶'}, {text:'Wrist Pain', icon:'👋'}, {text:'Ankle Issues', icon:'🦶'}] },
            { id: 'time', title: 'Cooking Time', desc: 'How much time for dinner?', options: [{text:'15 Mins (Quick)', icon:'⚡'}, {text:'30 Mins (Standard)', icon:'⏱️'}, {text:'45+ Mins (Chef)', icon:'👨‍🍳'}, {text:'Meal Prep (Batch)', icon:'📦'}] },
            { id: 'budget', title: 'Weekly Budget', desc: 'Target spending?', options: [{text:'Budget Friendly', icon:'💵'}, {text:'Moderate', icon:'💰'}, {text:'Premium (Organic)', icon:'💎'}] },

            // Deep Personalization (New)
            { id: 'sleep', title: 'Sleep Quality', desc: 'How do you typically sleep?', options: [{text:'Good / Restful', icon:'😴'}, {text:'Insomnia / Trouble Falling', icon:'👀'}, {text:'Light Sleeper', icon:'🔊'}, {text:'Night Owl', icon:'🦉'}, {text:'Early Bird', icon:'🐔'}] },
            { id: 'stress', title: 'Stress Levels', desc: 'Current stress load?', options: [{text:'Low / Zen', icon:'🧘'}, {text:'Moderate', icon:'😐'}, {text:'High Pressure', icon:'🤯'}, {text:'Burnout', icon:'🔥'}] },
            { id: 'hydration', title: 'Hydration Habits', desc: 'Water intake?', options: [{text:'Consistent', icon:'💧'}, {text:'Needs Improvement', icon:'🥤'}, {text:'Dehydrated', icon:'🌵'}, {text:'Coffee Dependent', icon:'☕'}] },
            { id: 'meals', title: 'Meal Frequency', desc: 'How often do you eat?', options: [{text:'3 Main Meals', icon:'🍽️'}, {text:'Grazer / Snacker', icon:'🍿'}, {text:'Intermittent Fasting (16:8)', icon:'⏱️'}, {text:'OMAD (One Meal)', icon:'🛑'}] },
            { id: 'cooking_skill', title: 'Cooking Skill', desc: 'Kitchen confidence?', options: [{text:'Beginner', icon:'👶'}, {text:'Intermediate', icon:'🍳'}, {text:'Advanced / Pro', icon:'👨‍🍳'}, {text:'Microwave Only', icon:'📠'}] },
            { id: 'motivation', title: 'Primary Motivation', desc: 'What drives you?', options: [{text:'Look Good', icon:'💅'}, {text:'Feel Good / Energy', icon:'⚡'}, {text:'Longevity', icon:'🐢'}, {text:'Mental Clarity', icon:'🧠'}, {text:'Athletic Performance', icon:'🏅'}] }
        ],

        // --- LIFECYCLE ---
        init() {
            localStorage.setItem('bio_token', this.token);

            // Restore Trackers
            const savedWater = localStorage.getItem('waterIntake');
            if (savedWater) this.waterIntake = parseInt(savedWater);
            const savedFasting = localStorage.getItem('fastingStart');
            if (savedFasting) { this.fastingStart = parseInt(savedFasting); this.startFastingTimer(); }
            const savedName = localStorage.getItem('userName');
            if(savedName) this.userName = savedName;

            // Init Calendar
            this.generateCalendar();
            this.selectedDate = this.calendarDays[0].fullDate;

            // Global Listeners
            document.addEventListener('mouseover', (e) => this.handleTooltipHover(e));

            // Watch Tab for Charts
            this.$watch('currentTab', (val) => {
                if (val === 'health') {
                    this.$nextTick(() => { this.renderCharts(); });
                }
            });
        },

        // --- CALENDAR LOGIC ---
        generateCalendar() {
            const today = new Date();
            const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
            for(let i=0; i<14; i++) {
                const d = new Date();
                d.setDate(today.getDate() + i);
                this.calendarDays.push({
                    day: days[d.getDay()],
                    date: d.getDate(),
                    fullDate: d.toISOString().split('T')[0],
                    active: i === 0
                });
            }
        },

        selectDate(dayObj) {
            this.selectedDate = dayObj.fullDate;
            this.calendarDays.forEach(d => d.active = (d.fullDate === dayObj.fullDate));
        },

        getMealsForSelectedDate() {
            if(!this.weekPlan.length) return [];
            const selectedIndex = this.calendarDays.findIndex(d => d.fullDate === this.selectedDate);
            if(selectedIndex >= 0 && selectedIndex < this.weekPlan.length) {
                return [this.weekPlan[selectedIndex]];
            }
            return [];
        },

        toggleMealCompletion(meal) {
            meal.completed = !meal.completed;
            if(meal.completed) this.notify("Meal Logged! Stats Updated.");
        },

        // --- LOADING LOGIC ---
        startLoading(phaseType) {
            this.loading = true;
            const thoughts = {
                'upload': ['Scanning PDF...', 'Extracting biomarkers...', 'Synthesizing health profile...'],
                'plan': ['Architecting Protocol...', 'Balancing Macros...', 'Finalizing Schedule...']
            };
            const phases = Array.isArray(phaseType) ? phaseType : (thoughts[phaseType] || thoughts['upload']);
            let i = 0;
            this.loadingText = phases[0];
            if(this.loadingInterval) clearInterval(this.loadingInterval);
            this.loadingInterval = setInterval(() => { i = (i + 1) % phases.length; this.loadingText = phases[i]; }, 1800);
        },

        stopLoading() { this.loading = false; clearInterval(this.loadingInterval); },

        // --- UPLOAD & CONSULTATION FLOW ---
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

                this.healthScore = this.context.health_score || 78;
                this.bloodMarkers = this.context.blood_markers || [];
                this.userName = this.context.patient_name || 'Guest';

                if (this.context.issues && this.context.issues.length > 0) {
                    this.startConsultation();
                } else {
                    this.finalizeConsultation();
                }
                this.notify("Analysis Complete");
            } catch(e) {
                this.notify("Upload Failed", "error");
            } finally {
                this.stopLoading();
            }
        },

        startConsultation() {
            this.consultationActive = true;
            this.consultationStep = 0;
            this.userChoices = {};
            this.bloodStrategies = [];

            const bioQueue = (this.context.issues || []).map(issue => ({
                type: 'bio',
                title: `${issue.title} Detected`,
                desc: issue.explanation,
                value: issue.value,
                options: issue.options.map(opt => ({ text: opt.text, icon: opt.type === 'Diet' ? '🥦' : '🧘' }))
            }));

            const lifeQueue = this.lifestyleQuestions.map(q => ({
                type: 'lifestyle', id: q.id, title: q.title, desc: q.desc, options: q.options
            }));

            this.interviewQueue = [...bioQueue, ...lifeQueue];
            this.currentQuestion = this.interviewQueue[0];
        },

        selectOption(option) {
            if (this.currentQuestion.type === 'bio') {
                this.bloodStrategies.push(option.text);
            } else {
                this.userChoices[this.currentQuestion.id] = option.text;
            }

            this.consultationStep++;
            if (this.consultationStep < this.interviewQueue.length) {
                this.currentQuestion = this.interviewQueue[this.consultationStep];
            } else {
                this.finalizeConsultation();
            }
        },

        async finalizeConsultation() {
            this.consultationActive = false;
            // First time generation uses "Personalized" default
            this.startLoading('plan');
            await this.executePlanGeneration("Personalized Protocol");
        },

        // --- MEAL WIZARD ---
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
                            lifestyle: this.userChoices
                        })
                    })
                ]);

                const data = await mealRes.json();
                this.workoutPlan = await workoutRes.json();

                this.weekPlan = data.map((daily, index) => {
                    const targetDate = new Date();
                    targetDate.setDate(new Date().getDate() + index);

                    // Initialize completed state for nested meals
                    const meals = daily.meals ? daily.meals.map(m => ({...m, completed: false})) : [];

                    return {
                        ...daily,
                        meals: meals,
                        date: targetDate.toISOString().split('T')[0],
                        completed: false
                    };
                });

                this.currentTab = 'dashboard';
                this.notify("Protocol Optimized");
            } catch(e) {
                this.notify("Generation Failed", "error");
            } finally {
                this.stopLoading();
            }
        },

        // --- CHAT ---
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
            } finally { this.chatLoading = false; }
        },

        typeWriterEffect(index, fullText) {
            return new Promise(resolve => {
                if(!fullText) { this.chatHistory[index].typing = false; resolve(); return; }
                let i = 0; const speed = 15;
                const type = () => {
                    if (i < fullText.length) {
                        this.chatHistory[index].text += fullText.charAt(i); i++;
                        this.scrollToBottom(); setTimeout(type, speed);
                    } else { this.chatHistory[index].typing = false; resolve(); }
                }; type();
            });
        },

        scrollToBottom() { this.$nextTick(() => { const c = document.getElementById('chat-container'); if(c) c.scrollTop = c.scrollHeight; }); },

        // --- TOOLTIPS ---
        handleTooltipHover(e) {
            const target = e.target.closest('[data-term]');
            if (!target) { this.tooltipVisible = false; this.activeTooltipTerm = null; return; }
            const term = target.getAttribute('data-term');
            if (this.activeTooltipTerm === term) { this.moveTooltip(e); this.tooltipVisible = true; return; }

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
                    if(this.activeTooltipTerm === term) this.tooltipText = data.response || data.definition || "No definition found.";
                } catch(err) { this.tooltipText = "Could not load definition."; }
            }, 300);
        },

        moveTooltip(e) {
            let x = e.clientX + 15; let y = e.clientY + 15;
            if (x > window.innerWidth - 260) x = e.clientX - 260;
            if (y > window.innerHeight - 100) y = e.clientY - 100;
            this.tooltipX = x; this.tooltipY = y;
        },

        // --- UTILS ---
        renderCharts() {
            if (this.bloodMarkers.length === 0) return;
            // Access global charts storage
            if (!window.bioCharts) window.bioCharts = {};

            this.bloodMarkers.forEach((marker, index) => {
                const ctx = document.getElementById('chart-' + index);
                if (!ctx) return;

                if (window.bioCharts[index]) {
                    window.bioCharts[index].destroy();
                }

                window.bioCharts[index] = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: ['My Value', 'Min', 'Max'],
                        datasets: [{
                            label: marker.name,
                            data: [marker.value, marker.ref_min, marker.ref_max],
                            backgroundColor: [
                                '#3b82f6',
                                'rgba(255, 255, 255, 0.1)',
                                'rgba(255, 255, 255, 0.1)'
                            ],
                            borderWidth: 0,
                            borderRadius: 6,
                            barPercentage: 0.6
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                            y: {
                                beginAtZero: true,
                                grid: { color: 'rgba(255, 255, 255, 0.05)' },
                                ticks: { color: 'rgba(255, 255, 255, 0.4)', font: { size: 10 } }
                            },
                            x: {
                                grid: { display: false },
                                ticks: { color: 'rgba(255, 255, 255, 0.4)', font: { size: 10 } }
                            }
                        }
                    }
                });
            });
        },

        saveSettings() { localStorage.setItem('userName', this.userName); this.notify("Settings Saved"); },
        notify(msg, type='success') { const id = Date.now(); this.toasts.push({ id, message: msg, type }); setTimeout(() => { this.toasts = this.toasts.filter(t => t.id !== id); }, 3000); },

        openPrefModal(strategy) { this.tempStrategy = strategy; this.prefModalOpen = true; },

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

        resetSystem() {
            if(confirm('Reset all data?')) { this.context = null; this.weekPlan = []; this.chatHistory = []; this.toasts = []; this.currentTab = 'dashboard'; localStorage.clear(); window.location.reload(); }
        },

        // --- BIOHACKS & TRACKERS ---
        selectTool(tool) { this.selectedTool = tool; this.toolInputs = {}; this.toolResult = null; },
        async runTool() {
            if(!this.selectedTool) return; this.toolLoading = true; this.toolResult = null;
            try {
                const res = await fetch(`/${this.selectedTool.id}`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(this.toolInputs) });
                const data = await res.json(); this.toolResult = this.formatResult(data);
            } catch(e) { this.toolResult = "Error connecting."; } finally { this.toolLoading = false; }
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
            let output = ""; for(const [key, val] of Object.entries(data)) { output += `${key.replace(/_/g, ' ').toUpperCase()}: ${val}\n`; } return output;
        },
        addWater() { if(this.waterIntake < this.waterGoal) { this.waterIntake++; localStorage.setItem('waterIntake', this.waterIntake); if(this.waterIntake === this.waterGoal) this.notify("Hydration Goal Met! 💧"); } },
        resetWater() { this.waterIntake = 0; localStorage.setItem('waterIntake', 0); },
        toggleFasting() { if (this.fastingStart) { this.fastingStart = null; localStorage.removeItem('fastingStart'); clearInterval(this.fastingInterval); this.fastingElapsed = ''; this.notify("Fasting Ended"); } else { this.fastingStart = Date.now(); localStorage.setItem('fastingStart', this.fastingStart); this.startFastingTimer(); this.notify("Fasting Started ⏳"); } },
        startFastingTimer() { this.updateFastingTimer(); this.fastingInterval = setInterval(() => { this.updateFastingTimer(); }, 60000); },
        updateFastingTimer() { if (!this.fastingStart) return; const diff = Date.now() - this.fastingStart; const hours = Math.floor(diff / (1000 * 60 * 60)); const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60)); this.fastingElapsed = `${hours}h ${minutes}m`; }
    }))
});