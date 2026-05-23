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

        const duration = 1200; // ms
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
    // 1. Attendance Trend Chart (Bar/Line Chart)
    const trendCtx = document.getElementById('attendanceTrendChart');
    if (trendCtx) {
        try {
            const labels = JSON.parse(trendCtx.getAttribute('data-labels') || '[]');
            const data = JSON.parse(trendCtx.getAttribute('data-values') || '[]');

            new Chart(trendCtx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Present Students',
                        data: data,
                        borderColor: '#4f46e5', // Indigo
                        backgroundColor: 'rgba(79, 70, 229, 0.1)',
                        borderWidth: 3,
                        pointBackgroundColor: '#4f46e5',
                        pointHoverRadius: 8,
                        pointRadius: 5,
                        fill: true,
                        tension: 0.3
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            backgroundColor: 'rgba(15, 23, 42, 0.9)',
                            titleFont: { size: 13, weight: 'bold' },
                            bodyFont: { size: 12 },
                            padding: 10,
                            displayColors: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                borderDash: [2, 4],
                                color: '#e2e8f0'
                            },
                            ticks: {
                                stepSize: 1,
                                color: '#64748b',
                                font: { size: 11 }
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            },
                            ticks: {
                                color: '#64748b',
                                font: { size: 11 }
                            }
                        }
                    }
                }
            });
        } catch (e) {
            console.error('Failed to initialize attendance trend chart:', e);
        }
    }

    // 2. Student Branch Distribution Chart (Doughnut Chart)
    const branchCtx = document.getElementById('branchDistributionChart');
    if (branchCtx) {
        try {
            const labels = JSON.parse(branchCtx.getAttribute('data-labels') || '[]');
            const data = JSON.parse(branchCtx.getAttribute('data-values') || '[]');

            // Modern color palette
            const colors = [
                '#4f46e5', // Indigo
                '#10b981', // Emerald
                '#f59e0b', // Amber
                '#f43f5e', // Rose
                '#06b6d4', // Cyan
                '#8b5cf6', // Violet
                '#3b82f6'  // Blue
            ];

            new Chart(branchCtx, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: colors.slice(0, labels.length),
                        borderWidth: 2,
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
                                boxWidth: 12,
                                padding: 15,
                                color: '#475569',
                                font: { size: 12 }
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(15, 23, 42, 0.9)',
                            padding: 10
                        }
                    },
                    cutout: '65%'
                }
            });
        } catch (e) {
            console.error('Failed to initialize branch distribution chart:', e);
        }
    }
}
