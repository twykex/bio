export function journalSlice() {
    return {
        // --- JOURNAL & MOOD STATE ---
        journalEntries: {},
        journalAnalysis: {},
        moodHistory: {},
        gratitudeEntries: {},
        currentMood: null,
        journalInput: '',
        gratitudeInputs: ['', '', ''],
        currentPrompt: '',
        promptVisible: false,
        meditationActive: false,
        meditationTimeLeft: 0,
        meditationDuration: 5,
        meditationInterval: null,
        showMeditation: false,
        isListening: false,
        recognition: null,

        promptsList: [
            "What made you smile today?",
            "What is one thing you learned today?",
            "What was the biggest challenge you faced today?",
            "Who are you grateful for today and why?",
            "What is a goal you made progress on today?",
            "Describe a moment of peace you felt today.",
            "What is something you want to improve tomorrow?",
            "What was the best meal you ate today?",
            "How did you take care of yourself today?",
            "What is a memory that brings you joy?"
        ],

        // --- METHODS ---
        saveJournal() {
            this.journalEntries[this.selectedDate] = this.journalInput;

            // Save Gratitude
            if (!this.gratitudeEntries) this.gratitudeEntries = {};
            // Filter empty strings
            const validGratitude = this.gratitudeInputs.filter(g => g && g.trim() !== '');
            if (validGratitude.length > 0) {
                this.gratitudeEntries[this.selectedDate] = validGratitude;
            } else {
                 delete this.gratitudeEntries[this.selectedDate];
            }

            localStorage.setItem('journalEntries', JSON.stringify(this.journalEntries));
            localStorage.setItem('gratitudeEntries', JSON.stringify(this.gratitudeEntries));
            localStorage.setItem('moodHistory', JSON.stringify(this.moodHistory));

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
            if(!this.moodHistory) this.moodHistory = {};
            this.moodHistory[this.selectedDate] = mood;
            localStorage.setItem('moodHistory', JSON.stringify(this.moodHistory));
            this.notify(`Mood Recorded: ${mood}`);
            this.logActivity(`Mood: ${mood}`, '🎭');
        },

        getNewPrompt() {
             const idx = Math.floor(Math.random() * this.promptsList.length);
             this.currentPrompt = this.promptsList[idx];
             this.promptVisible = true;
        },

        dismissPrompt() {
            this.promptVisible = false;
        },

        toggleSpeech() {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) {
                this.notify("Voice input not supported", "error");
                return;
            }

            if (this.isListening) {
                this.recognition.stop();
                this.isListening = false;
                return;
            }

            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false; // Stop after silence
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';

            this.recognition.onstart = () => {
                this.isListening = true;
                this.notify("Listening... 🎙️");
            };

            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                if (transcript) {
                    this.journalInput += (this.journalInput ? ' ' : '') + transcript;
                }
            };

            this.recognition.onerror = (event) => {
                console.error(event.error);
                this.isListening = false;
                this.notify("Voice Error", "error");
            };

            this.recognition.onend = () => {
                this.isListening = false;
            };

            this.recognition.start();
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
