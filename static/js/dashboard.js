document.addEventListener('DOMContentLoaded', () => {
    // Chart.js - Student Enrollment Chart
    const ctx = document.getElementById('enrollmentChart');
    if (ctx) {
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Class 6', 'Class 7', 'Class 8', 'Class 9', 'Class 10'],
                datasets: [{
                    label: 'Number of Students',
                    data: [55, 52, 60, 48, 45], // Example data
                    backgroundColor: 'rgba(13, 110, 253, 0.6)',
                    borderColor: 'rgba(13, 110, 253, 1)',
                    borderWidth: 1,
                    borderRadius: 5,
                }]
            },
            options: {
                responsive: true,
                scales: { y: { beginAtZero: true } },
                plugins: { legend: { display: false } }
            }
        });
    }
});