/**
 * VIVA ADMIN PORTAL - CHART.JS CONTROLLER
 * Professional dark analytics charts
 */

document.addEventListener('DOMContentLoaded', function () {
  // Common Chart Defaults
  if (typeof Chart !== 'undefined') {
    Chart.defaults.color = '#94A39D';
    Chart.defaults.font.family = "'Plus Jakarta Sans', sans-serif";
    Chart.defaults.plugins.tooltip.backgroundColor = '#1B2421';
    Chart.defaults.plugins.tooltip.borderColor = '#26332E';
    Chart.defaults.plugins.tooltip.borderWidth = 1;
    Chart.defaults.plugins.tooltip.padding = 12;
    Chart.defaults.plugins.tooltip.titleColor = '#F3F4F6';
    Chart.defaults.plugins.tooltip.bodyColor = '#94A39D';
  }

  // 1. Monthly Revenue Trend Chart (Line)
  const revCanvas = document.getElementById('monthlyRevenueChart');
  if (revCanvas && window.monthlyRevenueData) {
    const ctx = revCanvas.getContext('2d');
    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, 'rgba(163, 230, 53, 0.35)');
    gradient.addColorStop(1, 'rgba(163, 230, 53, 0.0)');

    new Chart(ctx, {
      type: 'line',
      data: {
        labels: window.monthlyRevenueData.labels,
        datasets: [{
          label: 'Revenue (₹)',
          data: window.monthlyRevenueData.revenues,
          borderColor: '#A3E635',
          backgroundColor: gradient,
          borderWidth: 3,
          fill: true,
          tension: 0.35,
          pointBackgroundColor: '#A3E635',
          pointBorderColor: '#1B2421',
          pointBorderWidth: 2,
          pointRadius: 5,
          pointHoverRadius: 7
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: {
            grid: { color: 'rgba(255, 255, 255, 0.04)' }
          },
          y: {
            grid: { color: 'rgba(255, 255, 255, 0.04)' },
            ticks: {
              callback: function (value) {
                return '₹' + value.toLocaleString();
              }
            }
          }
        }
      }
    });
  }

  // 2. Category Sales Distribution (Donut Chart)
  const catCanvas = document.getElementById('categoryDonutChart');
  if (catCanvas && window.categorySalesData) {
    new Chart(catCanvas, {
      type: 'doughnut',
      data: {
        labels: window.categorySalesData.labels,
        datasets: [{
          data: window.categorySalesData.sales,
          backgroundColor: [
            '#A3E635', '#22C55E', '#06B6D4', '#3B82F6',
            '#8B5CF6', '#EC4899', '#F59E0B', '#10B981'
          ],
          borderColor: '#1B2421',
          borderWidth: 3,
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '72%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              boxWidth: 12,
              padding: 14,
              font: { size: 12 }
            }
          }
        }
      }
    });
  }

  // 3. Order Status Distribution (Doughnut)
  const statusCanvas = document.getElementById('orderStatusChart');
  if (statusCanvas && window.orderStatusData) {
    new Chart(statusCanvas, {
      type: 'doughnut',
      data: {
        labels: Object.keys(window.orderStatusData),
        datasets: [{
          data: Object.values(window.orderStatusData),
          backgroundColor: [
            '#F59E0B', '#10B981', '#3B82F6', '#8B5CF6', '#22C55E', '#EF4444'
          ],
          borderColor: '#1B2421',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '65%',
        plugins: {
          legend: {
            position: 'right',
            labels: { boxWidth: 10, padding: 10 }
          }
        }
      }
    });
  }
});
