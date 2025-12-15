export function fitnessSlice() {
    return {
        // --- FITNESS STATE ---
        workoutHistory: {}, // format: { "Bench Press": [ {date, weight, reps}, ... ] }
        workoutPlan: [],
        restActive: false,
        restTimeLeft: 0,
        restTotalTime: 0,
        restInterval: null,
        fitnessWizardOpen: false,
        fitnessStrategies: [],
        selectedFitnessStrategy: null,

        // --- FITNESS METHODS ---
        getNextWorkout() {
             const activeDayObj = this.calendarDays.find(d => d.active);
             if (!activeDayObj) return null;

             // Fuzzy match: "Mon" matches "Monday"
             const activeDay = activeDayObj.day; // e.g., "Mon"
             return this.workoutPlan.find(w => w.day.startsWith(activeDay)) || null;
        },

        toggleExercise(ex) {
            ex.completed = !ex.completed;
            if(ex.completed) {
                this.notify("Exercise Complete! 💪");
                this.logActivity(`Did ${ex.name || 'exercise'}`, '💪');
            }
        },

        finishWorkout(workout) {
            let logCount = 0;
            if (workout.exercises) {
                workout.exercises.forEach(ex => {
                    if (ex.weight || ex.performedReps) {
                        const name = ex.name || "Unknown Exercise";

                        // Initialize array if new exercise
                        if (!this.workoutHistory[name] || !Array.isArray(this.workoutHistory[name])) {
                            this.workoutHistory[name] = [];
                        }

                        // Add new log entry
                        this.workoutHistory[name].push({
                            weight: ex.weight,
                            reps: ex.performedReps,
                            date: new Date().toISOString().split('T')[0],
                            notes: ex.notes
                        });
                        logCount++;
                    }
                });
            }
            localStorage.setItem('workoutHistory', JSON.stringify(this.workoutHistory));
            this.notify(logCount > 0 ? `Workout Saved! ${logCount} Logs Updated.` : "Workout Completed!");
            this.updateAchievement('workout_warrior', 1);
        },

        startRest(seconds) {
            if (this.restActive) {
                this.stopRest();
            }
            this.restTimeLeft = seconds;
            this.restTotalTime = seconds;
            this.restActive = true;
            if (this.restInterval) clearInterval(this.restInterval);
            this.restInterval = setInterval(() => {
                this.restTimeLeft--;
                if (this.restTimeLeft <= 0) {
                    this.stopRest();
                    this.notify("Rest Complete! Go!", "success");
                    // Play sound if desired
                    // const audio = new Audio('/static/sounds/beep.mp3'); audio.play();
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

            // Handle legacy data (if user had old object format)
            if (!Array.isArray(history)) return `Last: ${history.weight || '-'}kg`;

            if (history.length === 0) return null;

            const lastLog = history[history.length - 1];
            return `Last: ${lastLog.weight || '-'}kg x ${lastLog.reps || '-'} (${lastLog.date.substring(5)})`;
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
                    // Ensure day is standardized if needed, or keep as AI returned
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