/**
 * Dashboard Chart.js Line Rendering (Matching PDF Page 2)
 */
document.addEventListener('DOMContentLoaded', () => {
  const chartCanvas = document.getElementById('dashboardProgressChart');
  if (!chartCanvas || !window.dashboardData) return;

  const ctx = chartCanvas.getContext('2d');
  
  // Create gradient for score curve
  const gradient = ctx.createLinearGradient(0, 0, 0, 250);
  gradient.addColorStop(0, 'rgba(37, 99, 235, 0.25)');
  gradient.addColorStop(1, 'rgba(37, 99, 235, 0.0)');

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: window.dashboardData.labels,
      datasets: [
        {
          label: 'Mastery Score (%)',
          data: window.dashboardData.scores,
          borderColor: '#2563eb',
          backgroundColor: gradient,
          borderWidth: 2.5,
          fill: true,
          tension: 0.35,
          pointBackgroundColor: '#2563eb',
          pointBorderColor: '#ffffff',
          pointBorderWidth: 2,
          pointRadius: 4,
          pointHoverRadius: 6
        },
        {
          label: 'Accuracy (%)',
          data: window.dashboardData.accuracies,
          borderColor: '#06b6d4',
          borderDash: [5, 5],
          borderWidth: 2,
          fill: false,
          tension: 0.35,
          pointBackgroundColor: '#06b6d4',
          pointBorderColor: '#ffffff',
          pointBorderWidth: 2,
          pointRadius: 3,
          pointHoverRadius: 5
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top',
          align: 'end',
          labels: {
            boxWidth: 12,
            font: { family: 'Outfit, Inter', size: 11 }
          }
        },
        tooltip: {
          backgroundColor: '#0f172a',
          titleFont: { family: 'Outfit', size: 12 },
          bodyFont: { family: 'Inter', size: 12 },
          padding: 10,
          cornerRadius: 8,
          displayColors: true
        }
      },
      scales: {
        y: {
          min: 0,
          max: 100,
          ticks: {
            stepSize: 20,
            font: { family: 'Inter', size: 11 },
            callback: (value) => value + '%'
          },
          grid: {
            color: '#f1f5f9'
          }
        },
        x: {
          ticks: {
            font: { family: 'Inter', size: 11 }
          },
          grid: {
            display: false
          }
        }
      }
    }
  });
});
