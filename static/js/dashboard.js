/**
 * Dashboard JavaScript - Smart Attendance System
 * Implements real-time clock, count-up animations, and Chart.js visualizations.
 */

document.addEventListener('DOMContentLoaded', () => {
    // --- Real-time Clock ---
    initClock();

    // --- Count Up Animation for Stats ---
    initCountUp();

    // --- Chart.js Initializations ---
    initCharts();
});

/**
 * Initializes the real-time clock widget.
 */
function initClock() {
    const clockEl = document.getElementById('dashboard-clock');
    const dateEl = document.getElementById('dashboard-date');
    if (!clockEl) return;

    function updateTime() {
        const now = new Date();
        
        // Time in standard 12-hour format
        let hours = now.getHours();
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12;
        hours = hours ? hours : 12; // the hour '0' should be '12'
        const timeStr = `${hours}:${minutes}:${seconds} ${ampm}`;
        
        clockEl.textContent = timeStr;

        if (dateEl) {
            const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
            dateEl.textContent = now.toLocaleDateString('en-US', options);
        }
    }

    updateTime();
    setInterval(updateTime, 1000);
}

/**
 * Performs a smooth count-up animation on numerical statistics elements.
 */
function initCountUp() {
    const counters = document.querySelectorAll('.stat-count');
    
    counters.forEach(counter => {
        const target = +counter.getAttribute('data-target');
        if (isNaN(target)) return;

        const duration = 1000; // ms
        const stepTime = 15; // ms
        const steps = duration / stepTime;
        const increment = target / steps;
        let current = 0;

        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                counter.textContent = target.toLocaleString();
                clearInterval(timer);
            } else {
                counter.textContent = Math.floor(current).toLocaleString();
            }
        }, stepTime);
    });
}

/**
 * Initializes the Chart.js visual graphics if their containers are present on the page.
 */
function initCharts() {
    // 1. Weekly Attendance Trend Chart (Line Chart with Gradient Fill)
    const trendCtx = document.getElementById('attendanceTrendChart');
    if (trendCtx) {
        try {
            const labels = JSON.parse(trendCtx.getAttribute('data-labels') || '[]');
            const data = JSON.parse(trendCtx.getAttribute('data-values') || '[]');
            
            const ctx = trendCtx.getContext('2d');
            const gradient = ctx.createLinearGradient(0, 0, 0, 240);
            gradient.addColorStop(0, 'rgba(37, 99, 235, 0.2)');
            gradient.addColorStop(1, 'rgba(37, 99, 235, 0)');

            new Chart(trendCtx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Present Students',
                        data: data,
                        borderColor: '#2563eb', // Blue
                        backgroundColor: gradient,
                        borderWidth: 3,
                        pointBackgroundColor: '#2563eb',
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        pointHoverRadius: 8,
                        pointRadius: 4,
                        fill: true,
                        tension: 0.35
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            backgroundColor: 'rgba(15, 23, 42, 0.95)',
                            titleFont: { size: 12, weight: 'bold', family: 'Inter' },
                            bodyFont: { size: 12, family: 'Inter' },
                            padding: 10,
                            displayColors: false,
                            cornerRadius: 8
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                borderDash: [4, 4],
                                color: '#e2e8f0'
                            },
                            ticks: {
                                color: '#64748b',
                                font: { size: 10, family: 'Inter' }
                            }
                        },
                        x: {
                            grid: { display: false },
                            ticks: {
                                color: '#64748b',
                                font: { size: 10, family: 'Inter' }
                            }
                        }
                    }
                }
            });
        } catch (e) {
            console.error('Failed to initialize attendance trend chart:', e);
        }
    }

    // 2. Present/Absent Pie Chart (Doughnut Chart)
    const pieCtx = document.getElementById('presentAbsentPieChart');
    if (pieCtx) {
        try {
            const presentCount = parseInt(pieCtx.getAttribute('data-present') || '0', 10);
            const absentCount = parseInt(pieCtx.getAttribute('data-absent') || '4', 10);
            const totalCount = presentCount + absentCount;
            
            // Handle edge case where both are zero (e.g. empty DB)
            const chartData = totalCount === 0 ? [0, 1] : [presentCount, absentCount];
            const chartColors = totalCount === 0 ? ['#e2e8f0', '#ef4444'] : ['#22c55e', '#ef4444'];

            new Chart(pieCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Present', 'Absent'],
                    datasets: [{
                        data: chartData,
                        backgroundColor: chartColors,
                        borderWidth: 3,
                        borderColor: '#ffffff',
                        hoverOffset: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                boxWidth: 10,
                                padding: 15,
                                color: '#64748b',
                                font: { size: 11, family: 'Inter', weight: '500' }
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(15, 23, 42, 0.95)',
                            cornerRadius: 8,
                            padding: 10
                        }
                    },
                    cutout: '72%'
                }
            });
        } catch (e) {
            console.error('Failed to initialize present/absent distribution chart:', e);
        }
    }

    // 3. Monthly Trend Chart (Smooth Line Graph Charting Progress over time)
    const monthlyCtx = document.getElementById('monthlyTrendChart');
    if (monthlyCtx) {
        try {
            const ctx = monthlyCtx.getContext('2d');
            const gradient = ctx.createLinearGradient(0, 0, 0, 240);
            gradient.addColorStop(0, 'rgba(79, 70, 229, 0.2)');
            gradient.addColorStop(1, 'rgba(79, 70, 229, 0)');

            new Chart(monthlyCtx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
                    datasets: [{
                        label: 'Attendance %',
                        data: [78.5, 82.1, 80.4, 85.0, 84.6],
                        borderColor: '#4f46e5', // Accent Indigo
                        backgroundColor: gradient,
                        borderWidth: 3,
                        pointBackgroundColor: '#4f46e5',
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        pointHoverRadius: 8,
                        pointRadius: 4,
                        fill: true,
                        tension: 0.35
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            backgroundColor: 'rgba(15, 23, 42, 0.95)',
                            titleFont: { size: 12, weight: 'bold', family: 'Inter' },
                            bodyFont: { size: 12, family: 'Inter' },
                            padding: 10,
                            cornerRadius: 8,
                            displayColors: false
                        }
                    },
                    scales: {
                        y: {
                            min: 60,
                            max: 100,
                            grid: {
                                borderDash: [4, 4],
                                color: '#e2e8f0'
                            },
                            ticks: {
                                color: '#64748b',
                                font: { size: 10, family: 'Inter' },
                                callback: function(value) { return value + '%'; }
                            }
                        },
                        x: {
                            grid: { display: false },
                            ticks: {
                                color: '#64748b',
                                font: { size: 10, family: 'Inter' }
                            }
                        }
                    }
                }
            });
        } catch (e) {
            console.error('Failed to initialize monthly trend chart:', e);
        }
    }
}
