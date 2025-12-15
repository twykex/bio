import { lifestyleQuestions, toolsList, fitnessToolsList, dailyTips, quickPrompts } from './modules/config.js';
import { fitnessSlice } from './modules/fitness.js';
import { nutritionSlice } from './modules/nutrition.js';
import { chartsSlice } from './modules/charts.js';
import { journalSlice } from './modules/journal.js';
import { consultationSlice } from './modules/consultation.js';
import { utilsSlice } from './modules/utils.js';
import { apiSlice } from './modules/api.js';

// Define the main app function
const app = (userId) => ({
    // --- 1. CORE STATE ---
    token: userId || localStorage.getItem('bio_token') || Math.random().toString(36).substring(7),
    currentTab: 'dashboard',
    loading: false,
    loadingText: 'Initializing...',
    loadingInterval: null,
    userName: 'Guest',
    userChoices: {},
    preferences: '',
    tempStrategy: null,
    prefModalOpen: false,

    // --- 2. CONFIG DATA ---
    dailyTips,
    quickPrompts,
    lifestyleQuestions,
    tools: toolsList,
    fitnessTools: fitnessToolsList,
    currentTip: '',

    // --- 3. BIOHACK SEARCH STATE (FIXED) ---
    biohackSearch: '',
    biohackCategory: 'All',

    // --- 4. ACHIEVEMENTS DATA ---
    achievements: {
        'hydration_streak': { name: 'Hydration Hero', desc: 'Hit water goal 3 days in a row', icon: '💧', unlocked: false, progress: 0, target: 3 },
        'workout_warrior': { name: 'Workout Warrior', desc: 'Complete 5 workouts', icon: '💪', unlocked: false, progress: 0, target: 5 },
        'mindful_master': { name: 'Mindful Master', desc: 'Meditate for 30 mins total', icon: '🧘', unlocked: false, progress: 0, target: 30 },
        'streak_star': { name: 'Commitment King', desc: '7 Day Streak', icon: '🔥', unlocked: false, progress: 0, target: 7 }
    },

    // --- 5. MERGE MODULES ---
    ...apiSlice(),
    ...fitnessSlice(),
    ...nutritionSlice(),
    ...chartsSlice(),
    ...journalSlice(),
    ...consultationSlice(),
    ...utilsSlice(),

    // --- 6. CALENDAR STATE ---
    calendarDays: [],
    selectedDate: null,
    streak: 0,

    // --- 7. CHAT STATE ---
    chatInput: '',
    chatLoading: false,
    chatOpen: false,
    chatHistory: [],

    // --- 8. TOOLTIP STATE ---
    tooltipVisible: false,
    tooltipText: '',
    tooltipX: 0,
    tooltipY: 0,
    tooltipTimeout: null,
    activeTooltipTerm: null,

    // --- 9. LIFECYCLE & INIT ---
    init() {
        console.log("App Initialized");
        localStorage.setItem('bio_token', this.token);
        this.handleDailyStreak();
        this.restoreState();

        // Random Tip
        if(this.dailyTips && this.dailyTips.length) {
            this.currentTip = this.dailyTips[Math.floor(Math.random() * this.dailyTips.length)];
        }

        // Init Calendar
        this.generateCalendar();
        const todayStr = new Date().toISOString().split('T')[0];
        const foundDay = this.calendarDays.find(d => d.fullDate === todayStr);
        this.selectDate(foundDay || this.calendarDays[0]);

        // Global Listeners
        document.addEventListener('mouseover', (e) => this.handleTooltipHover(e));

        this.$watch('currentTab', (val) => {
            if(val === 'health') this.initCharts();
            if(val === 'dashboard') this.initDashboardCharts();
            if(val === 'nutrition') this.initNutritionCharts();
        });

        // Initial chart load
        if(this.currentTab === 'dashboard') this.initDashboardCharts();
    },

    // --- 10. BIOHACK HELPER (FIXED) ---
    getFilteredBiohacks() {
        if (!this.tools) return [];
        return this.tools.filter(tool => {
            const search = (this.biohackSearch || '').toLowerCase();
            const matchesSearch = tool.name.toLowerCase().includes(search) ||
                                  (tool.desc && tool.desc.toLowerCase().includes(search));
            const matchesCategory = (this.biohackCategory || 'All') === 'All' || tool.category === this.biohackCategory;
            return matchesSearch && matchesCategory;
        });
    },

    handleDailyStreak() {
        const lastLoginDate = localStorage.getItem('lastLoginDate');
        const todayStr = new Date().toISOString().split('T')[0];
        let currentStreak = parseInt(localStorage.getItem('userStreak') || '0');

        if (lastLoginDate !== todayStr) {
            const yesterday = new Date();
            yesterday.setDate(yesterday.getDate() - 1);
            const yesterdayStr = yesterday.toISOString().split('T')[0];

            if (lastLoginDate === yesterdayStr) {
                currentStreak++;
            } else {
                currentStreak = 1;
            }
            localStorage.setItem('userStreak', currentStreak);
            localStorage.setItem('lastLoginDate', todayStr);

            // Reset Daily Water
            this.waterIntake = 0;
            localStorage.setItem('waterIntake', 0);
        }
        this.streak = currentStreak;
        if(this.streak >= 7) this.updateAchievement('streak_star', 7);
    },

    restoreState() {
        const keys = [
            'context', 'weekPlan', 'workoutPlan', 'waterIntake',
            'userName', 'userChoices', 'journalEntries', 'journalAnalysis',
            'moodHistory', 'activityLog', 'waterHistory', 'achievements', 'workoutHistory'
        ];

        keys.forEach(key => {
            const val = localStorage.getItem(key);
            if (val) {
                try {
                    this[key] = (key === 'waterIntake' || key === 'userName') ? (key === 'waterIntake' ? parseInt(val) : val) : JSON.parse(val);
                } catch (e) { console.error(`Failed to restore ${key}`); }
            }
        });

        // Fasting restore
        const savedFasting = localStorage.getItem('fastingStart');
        if (savedFasting) { this.fastingStart = parseInt(savedFasting); this.startFastingTimer(); }

        // Sync current day water history
        const todayStr = new Date().toISOString().split('T')[0];
        if(this.waterIntake > 0 && this.waterHistory) this.waterHistory[todayStr] = this.waterIntake;
    },

    // --- 11. CALENDAR METHODS ---
    generateCalendar() {
        const today = new Date();
        const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        for(let i=-3; i<11; i++) {
            const d = new Date();
            d.setDate(today.getDate() + i);
            this.calendarDays.push({
                day: days[d.getDay()],
                date: d.getDate(),
                fullDate: d.toISOString().split('T')[0],
                active: i === 0,
                isToday: i === 0
            });
        }
    },

    selectDate(dayObj) {
        if(!dayObj) return;
        this.selectedDate = dayObj.fullDate;
        this.calendarDays.forEach(d => d.active = (d.fullDate === dayObj.fullDate));
        if(this.journalEntries) this.journalInput = this.journalEntries[this.selectedDate] || '';
        if(this.moodHistory) this.currentMood = this.moodHistory[this.selectedDate] || null;
        if(this.currentTab === 'nutrition') this.initNutritionCharts();
    },

    // --- 12. LOADING METHODS ---
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

    // --- 13. CHAT METHODS ---
    async sendMessage() {
        if(!this.chatInput.trim()) return;
        const msg = this.chatInput;
        this.chatHistory.push({ role: 'user', text: msg });
        this.chatInput = '';
        this.scrollToBottom();

        this.chatLoading = true;
        const aiIndex = this.chatHistory.push({ role: 'ai', text: '', typing: true }) - 1;

        try {
            const response = await fetch('/chat_agent', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ message: msg, token: this.token })
            });

            if (!response.ok) throw new Error('Network response was not ok');

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                this.chatHistory[aiIndex].text += chunk;
                this.scrollToBottom();
            }
            this.chatHistory[aiIndex].typing = false;

        } catch(e) {
            console.error(e);
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

    // --- 14. TOOLTIP METHODS ---
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
    }
});

// CRITICAL FIX: Bind to window AND register with Alpine
window.app = app;

document.addEventListener('alpine:init', () => {
    Alpine.data('app', app);
});