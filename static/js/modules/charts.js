export function chartsSlice() {
    return {
        radarChart: null,
        barChart: null,
        trendChart: null,
        moodChart: null,
        waterChart: null,
        nutritionDoughnut: null,
        nutritionTrend: null,

        async initDashboardCharts() {
            // Wait for DOM
            await this.$nextTick();
            const ctxMood = document.getElementById('moodTrendChart');
            const ctxWater = document.getElementById('waterHistoryChart');

            if (typeof Chart === 'undefined') return;

            // --- Mood Chart ---
            if(ctxMood) {
                if (this.moodChart) { this.moodChart.destroy(); this.moodChart = null; }

                // Generate last 7 days data
                const labels = [];
                const data = [];
                for(let i=6; i>=0; i--) {
                     const d = new Date();
                     d.setDate(new Date().getDate() - i);
                     const dateStr = d.toISOString().split('T')[0];
                     labels.push(d.toLocaleDateString(undefined, {weekday:'short'}));
                     const mood = this.moodHistory[dateStr];
                     let val = 0; // 0 = no data
                     if(mood === '😁') val = 4;
                     else if(mood === '🙂') val = 3;
                     else if(mood === '😐') val = 2;
                     else if(mood === '😔') val = 1;
                     data.push(val);
                }

                this.moodChart = new Chart(ctxMood, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Mood',
                            data: data,
                            borderColor: '#3b82f6',
                            backgroundColor: 'rgba(59, 130, 246, 0.1)',
                            fill: true,
                            tension: 0.4,
                            pointBackgroundColor: '#3b82f6'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: { display: false, min: 0, max: 5 },
                            x: { grid: { display: false }, ticks: { color: 'rgba(255, 255, 255, 0.3)', font: { size: 10 } } }
                        },
                        plugins: { legend: { display: false } }
                    }
                });
            }

            // --- Water Chart ---
            if(ctxWater) {
                if (this.waterChart) { this.waterChart.destroy(); this.waterChart = null; }

                const labels = [];
                const data = [];
                for(let i=6; i>=0; i--) {
                     const d = new Date();
                     d.setDate(new Date().getDate() - i);
                     const dateStr = d.toISOString().split('T')[0];
                     labels.push(d.toLocaleDateString(undefined, {weekday:'short'}));
                     data.push(this.waterHistory[dateStr] || 0);
                }

                this.waterChart = new Chart(ctxWater, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Glasses',
                            data: data,
                            backgroundColor: 'rgba(59, 130, 246, 0.5)',
                            borderRadius: 4,
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: { display: false, min: 0, suggestMax: 8 },
                            x: { grid: { display: false }, ticks: { color: 'rgba(255, 255, 255, 0.3)', font: { size: 10 } } }
                        },
                        plugins: { legend: { display: false } }
                    }
                });
            }
        },

        async initNutritionCharts() {
            if (typeof Chart === 'undefined') return;
            await this.$nextTick();

            const daily = this.getMealsForSelectedDate()[0];
            const ctxDoughnut = document.getElementById('dailyMacrosChart');
            const ctxTrend = document.getElementById('weeklyCalorieChart');

            if (this.nutritionDoughnut) { this.nutritionDoughnut.destroy(); this.nutritionDoughnut = null; }
            if (this.nutritionTrend) { this.nutritionTrend.destroy(); this.nutritionTrend = null; }

            // 1. Daily Macros Doughnut
            if (daily && ctxDoughnut) {
                const p = this.getMacroValue(daily.total_macros.protein);
                const c = this.getMacroValue(daily.total_macros.carbs);
                const f = this.getMacroValue(daily.total_macros.fats);

                this.nutritionDoughnut = new Chart(ctxDoughnut, {
                    type: 'doughnut',
                    data: {
                        labels: ['Protein', 'Carbs', 'Fats'],
                        datasets: [{
                            data: [p, c, f],
                            backgroundColor: ['#3b82f6', '#10b981', '#f97316'],
                            borderWidth: 0,
                            hoverOffset: 4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        cutout: '70%',
                        plugins: { legend: { display: false } }
                    }
                });
            }

            // 2. Weekly Trend
            if (this.weekPlan.length > 0 && ctxTrend) {
                const labels = this.weekPlan.map(d => new Date(d.date).toLocaleDateString(undefined, {weekday:'short'}));
                const data = this.weekPlan.map(d => this.getMacroValue(d.total_macros.calories));

                this.nutritionTrend = new Chart(ctxTrend, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Calories',
                            data: data,
                            borderColor: '#3b82f6',
                            backgroundColor: 'rgba(59, 130, 246, 0.1)',
                            fill: true,
                            tension: 0.4,
                            pointBackgroundColor: '#3b82f6'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: 'rgba(255, 255, 255, 0.4)' } },
                            x: { grid: { display: false }, ticks: { color: 'rgba(255, 255, 255, 0.4)' } }
                        },
                        plugins: { legend: { display: false } }
                    }
                });
            }
        },

        async initCharts() {
            if (!this.context || !this.context.biomarkers) return;

            // Wait for DOM update
            await this.$nextTick();

            const ctxRadar = document.getElementById('healthRadarChart');
            const ctxBar = document.getElementById('biomarkerBarChart');
            const ctxTrend = document.getElementById('healthTrendChart');

            if (this.radarChart) { this.radarChart.destroy(); this.radarChart = null; }
            if (this.barChart) { this.barChart.destroy(); this.barChart = null; }
            if (this.trendChart) { this.trendChart.destroy(); this.trendChart = null; }

            // -- Prepare Radar Data --
            const systems = {
                'Metabolism': 85,
                'Inflammation': 90,
                'Liver': 88,
                'Kidneys': 92,
                'Hormones': 75,
                'Lipids': 80
            };

            if(this.context.issues) {
                this.context.issues.forEach(issue => {
                     const t = issue.title || '';
                     if(t.includes('Lipid') || t.includes('Cholesterol')) systems['Lipids'] -= 20;
                     if(t.includes('Sugar') || t.includes('Glucose')) systems['Metabolism'] -= 20;
                     if(t.includes('Inflammation') || t.includes('CRP')) systems['Inflammation'] -= 20;
                });
            }

            // Ensure we don't crash if Chart is not loaded
            if (typeof Chart === 'undefined') return;

            this.radarChart = new Chart(ctxRadar, {
                type: 'radar',
                data: {
                    labels: Object.keys(systems),
                    datasets: [{
                        label: 'System Health',
                        data: Object.values(systems),
                        fill: true,
                        backgroundColor: 'rgba(59, 130, 246, 0.2)',
                        borderColor: 'rgb(59, 130, 246)',
                        pointBackgroundColor: 'rgb(59, 130, 246)',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: 'rgb(59, 130, 246)'
                    }]
                },
                options: {
                    scales: {
                        r: {
                            angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
                            grid: { color: 'rgba(255, 255, 255, 0.1)' },
                            pointLabels: { color: 'rgba(255, 255, 255, 0.7)', font: { size: 10 } },
                            ticks: { display: false, backdropColor: 'transparent' },
                            suggestedMin: 0,
                            suggestedMax: 100
                        }
                    },
                    plugins: { legend: { display: false } }
                }
            });

            // -- Prepare Bar Data --
            const labels = this.context.biomarkers.map(m => m.name);
            const statusValues = this.context.biomarkers.map(m => {
                const s = (m.status || '').toLowerCase();
                if(s === 'high') return 3;
                if(s === 'optimal' || s === 'normal') return 2;
                if(s === 'low') return 1;
                return 2;
            });

            const backgroundColors = this.context.biomarkers.map(m => {
                 const s = (m.status || '').toLowerCase();
                 if(s === 'high' || s === 'low') return 'rgba(239, 68, 68, 0.6)'; // Red
                 return 'rgba(16, 185, 129, 0.6)'; // Green
            });