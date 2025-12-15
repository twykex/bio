export function fitnessSlice() {
    return {
        // --- FITNESS STATE ---
        workoutHistory: {}, // format: { "Bench Press": [ {date, weight, reps, volume}, ... ] }
        workoutPlan: [],
        restActive: false,
        restTimeLeft: 0,
        restTotalTime: 0,
        restInterval: null,
        fitnessWizardOpen: false,
        fitnessStrategies: [],
        selectedFitnessStrategy: null,
        activeWorkoutMode: false,
        currentWorkoutVolume: 0,

        // NEW STATE
        fitnessToolOpen: false,
        activeFitnessTool: null,
        toolInputs: {},
        toolResult: null,
        fitnessChart: null,

        // --- INIT ---
        initFitness() {
            // Migration: Ensure all exercises have setLogs
            if (this.workoutPlan && this.workoutPlan.length) {
                let modified = false;
                this.workoutPlan.forEach(day => {
                    if (day.exercises) {
                        day.exercises.forEach(ex => {
                            if (!ex.setLogs) {
                                const numSets = parseInt(ex.sets) || 3;
                                ex.setLogs = Array.from({length: numSets}, (_, i) => ({
                                    id: i + 1,
                                    weight: ex.weight || '',
                                    reps: ex.performedReps || '',
                                    completed: ex.completed || false
                                }));
                                modified = true;
                            }
                        });
                    }
                });
                if (modified) {
                    localStorage.setItem('workoutPlan', JSON.stringify(this.workoutPlan));
                }
            }

            // Watch Tab for Chart
            this.$watch('currentTab', (val) => {
                if (val === 'fitness') {
                    setTimeout(() => this.initFitnessChart(), 200);
                }
            });
            // Initial load if already on fitness
            if (this.currentTab === 'fitness') setTimeout(() => this.initFitnessChart(), 200);
        },

        // --- NEW HELPERS ---
        isMuscleActive(part) {
            const workout = this.getNextWorkout();
            if (!workout || !workout.focus) return false;
            const focus = workout.focus.toLowerCase();
            const map = {
                'shoulders': ['push', 'upper', 'shoulders', 'full', 'arms', 'delts'],
                'chest': ['push', 'upper', 'chest', 'full', 'pecs'],
                'back': ['pull', 'upper', 'back', 'full', 'rows', 'lats'],
                'arms': ['push', 'pull', 'upper', 'arms', 'full', 'bicep', 'tricep'],
                'core': ['core', 'abs', 'full', 'stability'],
                'legs': ['legs', 'lower', 'full', 'squat', 'glute', 'hamstring', 'quad']
            };
            const p = part.toLowerCase();
            return map[p] ? map[p].some(k => focus.includes(k)) : false;
        },

        openFitnessTool(tool) {
            this.activeFitnessTool = tool;
            this.toolInputs = {};
            if (tool.inputs) {
                tool.inputs.forEach(i => this.toolInputs[i.k] = i.p);
            }
            this.toolResult = null;
            this.fitnessToolOpen = true;
        },

        runFitnessTool() {
            if (!this.activeFitnessTool) return;
            const id = this.activeFitnessTool.id;
            const inputs = this.toolInputs;

            if (id === 'calculate_1rm') {
                const w = parseFloat(inputs.weight);
                const r = parseFloat(inputs.reps);
                if (!w || !r) return;
                // Epley Formula
                const oneRM = w * (1 + r / 30);
                this.toolResult = `${Math.round(oneRM)} kg`;
            } else if (id === 'plate_calculator') {
                const target = parseFloat(inputs.weight);
                if (!target) return;
                const plates = this.calculatePlates(target);
                this.toolResult = plates.length ? plates.join(', ') : "Bar only (20kg)";
            } else if (id === 'heart_rate_zones') {
                 const age = parseFloat(inputs.age);
                 const max = 220 - age;
                 this.toolResult = `Max: ${max} bpm <br> <span class="text-sm text-white/50">Zone 2: ${Math.round(max * 0.6)}-${Math.round(max * 0.7)}</span>`;
            } else {
                this.toolResult = "Calculation complete.";
            }
        },

        calculatePlates(targetWeight) {
            // Assume 20kg bar
            let remaining = targetWeight - 20;
            if (remaining <= 0) return [];

            const plates = [20, 15, 10, 5, 2.5, 1.25];
            const toLoad = []; // per side

            remaining = remaining / 2; // per side

            plates.forEach(p => {
                while (remaining >= p) {
                    toLoad.push(`${p}kg`);
                    remaining -= p;
                }
            });

            return toLoad.length ? toLoad.map(p => `[${p}]`) : [];
        },

        initFitnessChart() {
             const ctx = document.getElementById('fitnessVolumeChart');
             if (!ctx) return;
             if (this.fitnessChart) {
                 this.fitnessChart.destroy();
                 this.fitnessChart = null;
             }

             // Calculate Weekly Volume from workoutHistory
             const volumeByDate = {};
             if (this.workoutHistory) {
                 Object.values(this.workoutHistory).flat().forEach(log => {
                     if (log.date) {
                         volumeByDate[log.date] = (volumeByDate[log.date] || 0) + (log.totalVolume || 0);
                     }
                 });
             }

             const labels = [];
             const data = [];
             const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

             // Show last 7 days relative to today
             for (let i = 6; i >= 0; i--) {
                 const d = new Date();
                 d.setDate(d.getDate() - i);
                 const dateStr = d.toISOString().split('T')[0];
                 const dayName = days[d.getDay()];
                 labels.push(dayName);
                 data.push(volumeByDate[dateStr] || 0);
             }

             this.fitnessChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Volume (kg)',
                        data: data,
                        backgroundColor: '#f97316',
                        borderRadius: 4,
                        barThickness: 12
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: {
                            display: true,
                            ticks: {
                                color: 'rgba(255,255,255,0.3)',
                                font: { size: 9 },
                                callback: function(value) { return value >= 1000 ? (value/1000).toFixed(1) + 'k' : value; }
                            },
                            grid: { color: 'rgba(255,255,255,0.05)' }
                        },
                        x: {
                            grid: { display: false },
                            ticks: { color: 'rgba(255,255,255,0.5)', font: { size: 10 } }
                        }
                    }
                }
             });
        },

        // --- COMPUTED / HELPERS ---
        getNextWorkout() {
             const activeDayObj = this.calendarDays.find(d => d.active);
             if (!activeDayObj) return null;
             const activeDay = activeDayObj.day;
             return this.workoutPlan.find(w => w.day.startsWith(activeDay)) || null;
        },

        calculateSessionVolume(dayPlan) {
            if (!dayPlan || !dayPlan.exercises) return 0;
            return dayPlan.exercises.reduce((acc, ex) => {
                const exVol = ex.setLogs.reduce((sAcc, set) => {
                    if (set.completed && set.weight && set.reps) {
                        return sAcc + (parseInt(set.weight) * parseInt(set.reps));
                    }
                    return sAcc;
                }, 0);
                return acc + exVol;
            }, 0);
        },

        // --- ACTIONS ---
        toggleSet(ex, setIndex) {
            const set = ex.setLogs[setIndex];
            set.completed = !set.completed;

            // Auto-fill from previous set if empty
            if (set.completed && setIndex > 0 && (!set.weight || !set.reps)) {
                const prev = ex.setLogs[setIndex - 1];
                if (!set.weight) set.weight = prev.weight;
                if (!set.reps) set.reps = prev.reps;
            }

            if (set.completed) {
                // Check if all sets completed
                const allDone = ex.setLogs.every(s => s.completed);
                if (allDone) {
                    this.notify(`${ex.name || 'Exercise'} Complete! 🔥`);
                    this.logActivity(`Finished ${ex.name}`, '💪');
                }
            }
            // Trigger reactivity for volume calculation (if we bind it)
            this.currentWorkoutVolume = this.calculateSessionVolume(this.getNextWorkout());

            // Re-calc today's volume in chart if needed (optional optimization: only update current day bar)
            if(this.currentTab === 'fitness') {
                // We could just update the chart data directly instead of full re-init
                // For now, simpler to re-init or leave it for finishWorkout
            }
        },

        finishWorkout(workout) {
            let logCount = 0;
            let totalVol = 0;

            if (workout.exercises) {
                workout.exercises.forEach(ex => {
                    const name = ex.name || "Unknown Exercise";
                    let bestSet = null;
                    let exVol = 0;

                    // Filter completed sets
                    const doneSets = ex.setLogs.filter(s => s.completed && s.weight && s.reps);

                    if (doneSets.length > 0) {
                        // Initialize history
                        if (!this.workoutHistory[name] || !Array.isArray(this.workoutHistory[name])) {
                            this.workoutHistory[name] = [];
                        }

                        // Calculate volume and find best set
                        doneSets.forEach(s => {
                            const vol = parseInt(s.weight) * parseInt(s.reps);
                            exVol += vol;
                            if (!bestSet || (parseInt(s.weight) > parseInt(bestSet.weight))) {
                                bestSet = s;
                            }
                        });

                        // Add log entry (summary of the session for this exercise)
                        this.workoutHistory[name].push({
                            date: new Date().toISOString().split('T')[0],
                            topWeight: bestSet.weight,
                            topReps: bestSet.reps,
                            totalVolume: exVol,
                            sets: doneSets.length,
                            notes: ex.notes
                        });
                        logCount++;
                        totalVol += exVol;
                    }
                });
            }

            localStorage.setItem('workoutHistory', JSON.stringify(this.workoutHistory));

            if (logCount > 0) {
                this.notify(`Workout Saved! Volume: ${totalVol}kg`, "success");
                this.updateAchievement('workout_warrior', 1);
                // Refresh chart to show new volume
                this.initFitnessChart();
            } else {
                this.notify("Workout Completed (No Data Logged)");
            }

            this.activeWorkoutMode = false;
        },

        startRest(seconds) {
            if (this.restActive) this.stopRest();
            this.restTimeLeft = seconds;
            this.restTotalTime = seconds;
            this.restActive = true;
            if (this.restInterval) clearInterval(this.restInterval);
            this.restInterval = setInterval(() => {
                this.restTimeLeft--;
                if (this.restTimeLeft <= 0) {
                    this.stopRest();
                    this.notify("Rest Complete! Go!", "success");
                    const audio = new Audio('https://assets.mixkit.co/sfx/preview/mixkit-software-interface-start-2574.mp3');
                    audio.volume = 0.5;
                    audio.play().catch(e => console.log("Audio play failed"));
                }
            }, 1000);
        },

        stopRest() {
            this.restActive = false;
            clearInterval(this.restInterval);
        },

        get formattedRestTime() {
            const m = Math.floor(this.restTimeLeft / 60);
            const s = this.restTimeLeft % 60;
            return `${m}:${s < 10 ? '0' + s : s}`;
        },

        getExerciseHistory(exName) {
            if (!this.workoutHistory || !this.workoutHistory[exName]) return null;
            const history = this.workoutHistory[exName];
            if (!Array.isArray(history) || history.length === 0) return null;

            const lastLog = history[history.length - 1];
            // Support both old format (weight/reps direct) and new format (topWeight/topReps)
            const w = lastLog.topWeight || lastLog.weight || '-';
            const r = lastLog.topReps || lastLog.reps || '-';
            return `${w}kg x ${r}`;
        },

        getExerciseProgress(exName) {
             // Returns a trend: 'up', 'down', 'same' based on volume or weight
             if (!this.workoutHistory || !this.workoutHistory[exName]) return 'same';
             const h = this.workoutHistory[exName];
             if (h.length < 2) return 'same';
             const last = h[h.length - 1];
             const prev = h[h.length - 2];
             const lastW = parseInt(last.topWeight || last.weight || 0);
             const prevW = parseInt(prev.topWeight || prev.weight || 0);
             return lastW > prevW ? 'up' : (lastW < prevW ? 'down' : 'same');
        },

        async openFitnessWizard() {
            this.fitnessWizardOpen = true;
            this.fitnessStrategies = [];
            this.startLoading(['Analyzing Physique...', 'Designing Splits...']);
            try {
                const res = await fetch('/propose_fitness_strategies', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ token: this.token, lifestyle: this.userChoices })
                });
                this.fitnessStrategies = await res.json();
            } catch(e) {
                this.notify("AI Trainer Offline", "error");
                this.fitnessWizardOpen = false;
            } finally {
                this.stopLoading();
            }
        },

        async selectFitnessStrategy(strat) {
            this.fitnessWizardOpen = false;
            this.selectedFitnessStrategy = strat;
            await this.generateWorkoutOnly();
        },

        async generateWorkoutOnly() {
            this.startLoading(['Analyzing Physique...', 'Designing Hypertrophy...', 'Scheduling Rest...']);
            try {
                const res = await fetch('/generate_workout', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        token: this.token,
                        strategy_name: 'Reshuffle',
                        fitness_strategy: this.selectedFitnessStrategy?.title || 'Personalized Split',
                        lifestyle: this.userChoices
                    })
                });
                const workoutData = await res.json();

                // Normalize data structure
                this.workoutPlan = workoutData.map(daily => ({
                    ...daily,
                    exercises: daily.exercises ? daily.exercises.map(ex => {
                        const exObj = (typeof ex === 'string') ? { name: ex } : ex;
                        const numSets = parseInt(exObj.sets) || 3;
                        return {
                            ...exObj,
                            sets: numSets, // Ensure numeric
                            setLogs: Array.from({length: numSets}, (_, i) => ({
                                id: i + 1,
                                weight: '',
                                reps: '',
                                completed: false
                            })),
                            notes: ''
                        };
                    }) : []
                }));
                localStorage.setItem('workoutPlan', JSON.stringify(this.workoutPlan));

                this.notify("New Training Plan Ready");
            } catch(e) {
                console.error(e);
                this.notify("Failed to update workout", "error");
            } finally {
                this.stopLoading();
            }
        }
    }
}
