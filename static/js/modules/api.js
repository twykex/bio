export function apiSlice() {
    return {
        // --- API & UPLOAD METHODS ---

        async uploadFile(e) {
            const file = e.target.files[0];
            if (!file) return;

            // 1. Start UI Loading State
            this.startLoading('upload');

            const formData = new FormData();
            formData.append('file', file);
            formData.append('token', this.token);

            try {
                // 2. Send to Backend
                const res = await fetch('/init_context', {
                    method: 'POST',
                    body: formData
                });

                if (!res.ok) throw new Error('Upload failed');

                const data = await res.json();
                this.handleAnalysisSuccess(data);

            } catch (err) {
                console.error(err);
                this.notify("Error analyzing PDF.", "error");
                this.stopLoading();
            }
        },

        async loadDemoData() {
            this.startLoading('upload');
            try {
                const res = await fetch('/load_demo_data', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ token: this.token })
                });

                const data = await res.json();
                this.handleAnalysisSuccess(data);

            } catch (err) {
                console.error(err);
                this.notify("Could not load demo.", "error");
                this.stopLoading();
            }
        },

        handleAnalysisSuccess(data) {
            // 3. Save the specific bloodwork data
            this.context = data;
            localStorage.setItem('context', JSON.stringify(data));

            // Update Metrics
            this.healthScore = this.context.health_score || 75;
            this.userName = this.context.patient_name || 'Guest';
            if(this.updateBioMetrics) this.updateBioMetrics();

            // 4. Generate a placeholder "Week Plan" to trigger the Dashboard View
            // (In a full app, you might fetch a specific plan from another endpoint here)
            this.weekPlan = [
                { day: 'Monday', focus: 'Metabolic Reset', workout: 'Zone 2 Cardio', meal: 'Low Carb' },
                { day: 'Tuesday', focus: 'Recovery', workout: 'Yoga', meal: 'Balanced' },
                { day: 'Wednesday', focus: 'Strength', workout: 'Upper Body', meal: 'High Protein' }
            ];
            localStorage.setItem('weekPlan', JSON.stringify(this.weekPlan));

            // 5. Success!
            this.stopLoading();
            this.notify("Analysis Complete! 🧬");
            this.showOnboarding = true;
        }
    }
}