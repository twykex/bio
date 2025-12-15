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

            // Generate dates for the next 7 days
            const today = new Date();
            const days = [];
            for (let i = 0; i < 7; i++) {
                const d = new Date(today);
                d.setDate(today.getDate() + i);
                days.push({
                    day: d.toLocaleDateString('en-US', { weekday: 'short' }),
                    date: d.toISOString().split('T')[0],
                    fullDate: d.toISOString().split('T')[0]
                });
            }

            this.weekPlan = days.map(d => ({
                day: d.day,
                date: d.date,
                fullDate: d.fullDate,
                completed: false,
                meals: [
                    { type: 'Breakfast', title: 'Oatmeal & Berries', calories: '350', protein: '12g', carbs: '60g', fats: '6g', completed: false },
                    { type: 'Lunch', title: 'Grilled Chicken Salad', calories: '450', protein: '40g', carbs: '15g', fats: '20g', completed: false },
                    { type: 'Dinner', title: 'Salmon & Asparagus', calories: '500', protein: '35g', carbs: '10g', fats: '25g', completed: false },
                    { type: 'Snack', title: 'Almonds', calories: '160', protein: '6g', carbs: '6g', fats: '14g', completed: false }
                ],
                total_macros: { calories: 1460, protein: '93g', carbs: '91g', fats: '65g' }
            }));

            localStorage.setItem('weekPlan', JSON.stringify(this.weekPlan));

            // 5. Success!
            this.stopLoading();
            this.notify("Analysis Complete! 🧬");
            this.showOnboarding = true;
        }
    }
}
