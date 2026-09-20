/**
 * Progress & Analytics Page Chart.js Visualizations
 */
document.addEventListener('DOMContentLoaded', () => {
  if (!window.progressData) return;

  // 1. Score & Accuracy Trend Chart
  const trendCanvas = document.getElementById('progressTrendChart');
  if (trendCanvas) {
    const ctx = trendCanvas.getContext('2d');
    
    const gradScore = ctx.createLinearGradient(0, 0, 0, 280);
    gradScore.addColorStop(0, 'rgba(37, 99, 235, 0.25)');
    gradScore.addColorStop(1, 'rgba(37, 99, 235, 0.0)');

    new Chart(ctx, {
      type: 'line',
      data: {
        labels: window.progressData.dates,
        datasets: [
          {
            label: 'Score (%)',
            data: window.progressData.scores,
            borderColor: '#2563eb',
            backgroundColor: gradScore,
            borderWidth: 3,
            fill: true,
            tension: 0.35,
            pointBackgroundColor: '#2563eb',
            pointRadius: 4
          },
          {
            label: 'Accuracy (%)',
            data: window.progressData.accuracies,
            borderColor: '#06b6d4',
            borderWidth: 2,
            borderDash: [4, 4],
            fill: false,
            tension: 0.35,
            pointBackgroundColor: '#06b6d4',
            pointRadius: 3
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            align: 'end',
            labels: { font: { family: 'Outfit, Inter', size: 11 } }
          }
        },
        scales: {
          y: {
            min: 0,
            max: 100,
            ticks: {
              stepSize: 20,
              callback: v => v + '%'
            },
            grid: { color: '#f1f5f9' }
          },
          x: { grid: { display: false } }
        }
      }
    });
  }

  // 2. Subject Radar Chart
  const radarCanvas = document.getElementById('subjectRadarChart');
  if (radarCanvas && window.progressData.subjectScores) {
    const ctxRadar = radarCanvas.getContext('2d');
    const subjects = Object.keys(window.progressData.subjectScores);
    const scores = Object.values(window.progressData.subjectScores);

    new Chart(ctxRadar, {
      type: 'radar',
      data: {
        labels: subjects,
        datasets: [{
          label: 'Proficiency (%)',
          data: scores,
          backgroundColor: 'rgba(99, 102, 241, 0.2)',
          borderColor: '#6366f1',
          pointBackgroundColor: '#6366f1',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: '#6366f1',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            angleLines: { color: '#e2e8f0' },
            grid: { color: '#f1f5f9' },
            pointLabels: {
              font: { family: 'Outfit, Inter', size: 10 }
            },
            min: 0,
            max: 100,
            ticks: { display: false, stepSize: 25 }
          }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  }
});
