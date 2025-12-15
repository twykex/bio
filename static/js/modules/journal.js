export function journalSlice() {
    return {
        // --- JOURNAL & MOOD STATE ---
        journalEntries: {},
        journalAnalysis: {},
        moodHistory: {},
        currentMood: null,
        journalInput: '',
        meditationActive: false,
        meditationTimeLeft: 0,
        meditationDuration: 5,
        meditationInterval: null,
        showMeditation: false,

        // --- METHODS ---
        saveJournal() {
            this.journalEntries[this.selectedDate] = this.journalInput;
            localStorage.setItem('journalEntries', JSON.stringify(this.journalEntries));
            this.notify("Journal Saved ✍️");
            this.logActivity("Wrote in journal", '✍️');
        },

        async analyzeJournal() {
             if(!this.journalInput.trim()) return;
             this.notify("Analyzing Entry... 🧠");
             try {
                 const res = await fetch('/analyze_journal', {
                     method: 'POST',
                     headers: {'Content-Type': 'application/json'},
                     body: JSON.stringify({ entry: this.journalInput })
                 });
                 const data = await res.json();

                 if(!this.journalAnalysis) this.journalAnalysis = {};
                 this.journalAnalysis[this.selectedDate] = data;
                 localStorage.setItem('journalAnalysis', JSON.stringify(this.journalAnalysis));

                 this.notify("Analysis Complete ✨");
             } catch(e) {
                 this.notify("Analysis Failed", "error");
             }
        },

        setMood(mood) {
            this.currentMood = mood;
            this.moodHistory[this.selectedDate] = mood;
            localStorage.setItem('moodHistory', JSON.stringify(this.moodHistory));
            this.notify(`Mood Recorded: ${mood}`);
            this.logActivity(`Mood: ${mood}`, '🎭');
        },

        toggleMeditation() {
            this.showMeditation = !this.showMeditation;
            if(!this.showMeditation) {
                this.stopMeditation();
            }
        },

        startMeditation() {
            if(this.meditationActive) return;
            this.meditationActive = true;
            this.meditationTimeLeft = this.meditationDuration * 60;
            this.meditationInterval = setInterval(() => {
                this.meditationTimeLeft--;
                if(this.meditationTimeLeft <= 0) {
                    this.stopMeditation();
                    this.notify("Meditation Complete 🧘");
                    this.logActivity(`Meditated ${this.meditationDuration}m`, '🧘');
                    this.updateAchievement('mindful_master', this.meditationDuration);
                }
            }, 1000);
        },

        stopMeditation() {
            this.meditationActive = false;
            clearInterval(this.meditationInterval);
        },

        get formattedMeditationTime() {
            const m = Math.floor(this.meditationTimeLeft / 60);
            const s = this.meditationTimeLeft % 60;
            return `${m}:${s < 10 ? '0' + s : s}`;
        }
    }
}