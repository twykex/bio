export function consultationSlice() {
    return {
        // --- CONSULTATION & UPLOAD STATE ---
        context: null,
        consultationActive: false,
        consultationStep: 0,
        interviewQueue: [],
        currentQuestion: null,
        bloodStrategies: [],
        dragOver: false,
        healthScore: 85,
        sleepScore: 78,
        hrv: 45,
        rhr: 62,
        biologicalAge: 0,
        chronologicalAge: 30,
        healthHistory: [],

        // --- METHODS ---
        handleDrop(e) {
            this.dragOver = false;
            const file = e.dataTransfer.files[0];
            if (file) this.uploadData(file);
        },

        async loadDemoData() {
            this.startLoading(['Loading Sample Profile...', 'Simulating Analysis...', 'Synthesizing Health Data...']);

            try {
                const res = await fetch('/load_demo_data', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ token: this.token })
                });
                if(!res.ok) throw new Error();
                this.context = await res.json();
                localStorage.setItem('context', JSON.stringify(this.context));

                this.healthScore = this.context.health_score || 72;
                this.userName = this.context.patient_name || 'Demo User';
                this.updateBioMetrics();

                // Simulate delay for effect
                await new Promise(r => setTimeout(r, 1500));

                if (this.context.issues && this.context.issues.length > 0) {
                    this.startConsultation();
                } else {
                    this.finalizeConsultation();
                }
                this.notify("Demo Loaded Successfully");
            } catch(e) {
                this.notify("Demo Failed", "error");
            } finally {
                this.stopLoading();
            }
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
                localStorage.setItem('context', JSON.stringify(this.context));

                this.healthScore = this.context.health_score || 78;
                this.userName = this.context.patient_name || 'Guest';
                this.updateBioMetrics();

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
                localStorage.setItem('userChoices', JSON.stringify(this.userChoices));
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

        updateBioMetrics() {
             const ageMap = { '18-29': 24, '30-39': 35, '40-49': 45, '50-59': 55, '60+': 65 };
             const userAgeStr = this.userChoices?.age || '30-39';
             this.chronologicalAge = ageMap[userAgeStr] || 30;

             // Bio Age Formula: ChronAge * (1 + (75 - Score)/200) -- scaled down impact
             const impact = (75 - this.healthScore) / 200;
             this.biologicalAge = (this.chronologicalAge * (1 + impact)).toFixed(1);

             // Update Mock Metrics based on Health Score
             this.sleepScore = Math.min(100, Math.max(50, Math.floor(this.healthScore * 0.9 + (Math.random() * 10))));
             this.hrv = Math.floor(this.healthScore * 0.6 + 10);
             this.rhr = Math.floor(80 - (this.healthScore * 0.2));

             this.healthHistory = this.generateHealthHistory();
        },

        getBiomarkersByCategory(category) {
            if (!this.context || !this.context.biomarkers) return [];
            return this.context.biomarkers.filter(b => {
                const n = b.name.toLowerCase();
                if (category === 'Metabolic') return ['glucose', 'hba1c', 'insulin', 'cholesterol', 'triglycerides', 'ldl', 'hdl'].some(k => n.includes(k));
                if (category === 'Hormonal') return ['cortisol', 'testosterone', 'estrogen', 'tsh', 'thyroid'].some(k => n.includes(k));
                if (category === 'Inflammation') return ['crp', 'ferritin', 'homocysteine'].some(k => n.includes(k));
                if (category === 'Nutrients') return ['vitamin', 'iron', 'magnesium', 'zinc', 'sodium', 'potassium'].some(k => n.includes(k));
                return false;
            });
        },

        generateHealthHistory() {
            const history = [];
            const today = new Date();
            let currentScore = this.healthScore;
            // Generate last 6 months
            for(let i=0; i<6; i++) {
                const d = new Date();
                d.setMonth(today.getMonth() - i);
                // Mock historical variation
                const variance = Math.floor(Math.random() * 10) - 5;
                let score = currentScore - (i * 2) + variance;
                if(score > 100) score = 100;
                if(score < 40) score = 40;
                if(i === 0) score = this.healthScore;

                history.unshift({ date: d.toLocaleDateString(undefined, {month:'short'}), score: score });
            }
            return history;
        }
    }
}