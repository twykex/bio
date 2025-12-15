export function utilsSlice() {
    return {
        // --- UTILS & GLOBAL STATE ---
        toasts: [],
        activityLog: [],
        waterHistory: {},
        waterIntake: 0,
        waterGoal: 8,
        fastingStart: null,
        fastingElapsed: '',
        fastingInterval: null,

        // --- BIOHACK TOOLS ---
        selectedTool: null,
        toolInputs: {},
        toolResult: null,
        toolLoading: false,
        biohackCategory: 'All',
        biohackSearch: '',
        bioHacksOpen: false,

        // --- METHODS ---
        notify(msg, type='success') {
            const id = Date.now();
            this.toasts.push({ id, message: msg, type });
            setTimeout(() => { this.toasts = this.toasts.filter(t => t.id !== id); }, 3000);
        },

        logActivity(text, icon="📌") {
            const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            this.activityLog.unshift({ text, time, icon });
            if(this.activityLog.length > 20) this.activityLog.pop();
            localStorage.setItem('activityLog', JSON.stringify(this.activityLog));
        },

        saveSettings() {
            localStorage.setItem('userName', this.userName);
            localStorage.setItem('userChoices', JSON.stringify(this.userChoices));
            this.notify("Settings Saved");
        },

        resetSystem() {
            if(confirm('Reset all data?')) { this.context = null; this.weekPlan = []; this.chatHistory = []; this.toasts = []; this.currentTab = 'dashboard'; localStorage.clear(); window.location.reload(); }
        },

        exportData() {
            const data = {
                context: this.context,
                weekPlan: this.weekPlan,
                workoutPlan: this.workoutPlan,
                workoutHistory: this.workoutHistory,
                journalEntries: this.journalEntries,
                journalAnalysis: this.journalAnalysis,
                userChoices: this.userChoices,
                achievements: this.achievements,
                waterHistory: this.waterHistory,
                moodHistory: this.moodHistory,
                activityLog: this.activityLog
            };
            const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `bioflow_data_${new Date().toISOString().split('T')[0]}.json`;
            a.click();
            URL.revokeObjectURL(url);
            this.notify("Data Exported 📥");
        },

        // --- WATER TRACKER ---
        addWater() {
            if(this.waterIntake < this.waterGoal) {
                this.waterIntake++;
                localStorage.setItem('waterIntake', this.waterIntake);

                const today = new Date().toISOString().split('T')[0];
                this.waterHistory[today] = this.waterIntake;
                localStorage.setItem('waterHistory', JSON.stringify(this.waterHistory));
                this.logActivity(`Drank water`, '💧');

                // Update chart if exists
                if(this.waterChart) {
                    const data = this.waterChart.data.datasets[0].data;
                    data[data.length - 1] = this.waterIntake;
                    this.waterChart.update();
                }

                if(this.waterIntake === this.waterGoal) {
                    this.notify("Hydration Goal Met! 💧");
                    this.updateAchievement('hydration_streak', 1);
                    this.logActivity("Hit hydration goal!", '🏆');
                }
            }
        },
        resetWater() { this.waterIntake = 0; localStorage.setItem('waterIntake', 0); },

        // --- FASTING ---
        toggleFasting() { if (this.fastingStart) { this.fastingStart = null; localStorage.removeItem('fastingStart'); clearInterval(this.fastingInterval); this.fastingElapsed = ''; this.notify("Fasting Ended"); } else { this.fastingStart = Date.now(); localStorage.setItem('fastingStart', this.fastingStart); this.startFastingTimer(); this.notify("Fasting Started ⏳"); } },
        startFastingTimer() { this.updateFastingTimer(); this.fastingInterval = setInterval(() => { this.updateFastingTimer(); }, 60000); },
        updateFastingTimer() { if (!this.fastingStart) return; const diff = Date.now() - this.fastingStart; const hours = Math.floor(diff / (1000 * 60 * 60)); const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60)); this.fastingElapsed = `${hours}h ${minutes}m`; },

        // --- TOOLS ---
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

        // --- ACHIEVEMENTS ---
        updateAchievement(id, amount) {
            if(this.achievements[id] && !this.achievements[id].unlocked) {
                this.achievements[id].progress += amount;
                if(this.achievements[id].progress >= this.achievements[id].target) {
                    this.achievements[id].unlocked = true;
                    this.notify(`Achievement Unlocked: ${this.achievements[id].name}! 🏆`);
                }
                localStorage.setItem('achievements', JSON.stringify(this.achievements));
            }
        },

        openPrefModal(strategy) { this.tempStrategy = strategy; this.prefModalOpen = true; }
    }
}