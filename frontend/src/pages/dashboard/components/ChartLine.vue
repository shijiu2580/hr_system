<template>
  <div class="chart-wrapper">
    <canvas ref="canvas"></canvas>
  </div>
</template>
<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue';
import { Chart } from 'chart.js/auto';

const props = defineProps({
  labels: { type: Array, default: () => [] },
  series: { type: Object, default: () => ({ total: [], late: [], absent: [] }) },
  height: { type: Number, default: 200 },
});

const canvas = ref(null);
let chartInstance = null;

function build(){
  if(!canvas.value) return;
  const ctx = canvas.value.getContext('2d');
  const dataSets = [];
  
  if(props.series.total?.length){
    dataSets.push({ 
      label: '记录数', 
      data: props.series.total, 
      borderColor: '#4f7cac',
      backgroundColor: 'rgba(79, 124, 172, 0.08)',
      borderWidth: 2,
      tension: 0.3,
      fill: true,
      pointRadius: 2,
      pointBackgroundColor: '#4f7cac',
      pointHoverRadius: 4,
    });
  }
  
  if(props.series.late?.length){
    dataSets.push({ 
      label: '迟到', 
      data: props.series.late, 
      borderColor: '#e09145',
      backgroundColor: 'transparent',
      borderWidth: 1.5,
      tension: 0.3,
      fill: false,
      pointRadius: 2,
      pointBackgroundColor: '#e09145',
      pointHoverRadius: 4,
    });
  }
  
  if(props.series.absent?.length){
    dataSets.push({ 
      label: '缺勤', 
      data: props.series.absent, 
      borderColor: '#c75c5c',
      backgroundColor: 'transparent',
      borderWidth: 1.5,
      tension: 0.3,
      fill: false,
      pointRadius: 2,
      pointBackgroundColor: '#c75c5c',
      pointHoverRadius: 4,
    });
  }
  
  if(chartInstance){ chartInstance.destroy(); }
  
  chartInstance = new Chart(ctx, {
    type: 'line',
    data: { labels: props.labels, datasets: dataSets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { 
        legend: { 
          display: true,
          position: 'top',
          align: 'end',
          labels: {
            usePointStyle: true,
            pointStyle: 'line',
            padding: 12,
            font: { size: 11 },
            color: '#666',
            boxWidth: 20,
          }
        },
        tooltip: {
          backgroundColor: '#fff',
          titleColor: '#333',
          bodyColor: '#666',
          borderColor: '#e5e5e5',
          borderWidth: 1,
          titleFont: { size: 12 },
          bodyFont: { size: 11 },
          padding: 10,
          cornerRadius: 4,
          displayColors: true,
          boxWidth: 12,
        }
      },
      interaction: { 
        mode: 'index', 
        intersect: false,
      },
      scales: { 
        x: {
          grid: { display: false },
          ticks: {
            font: { size: 10 },
            color: '#999',
            maxRotation: 0,
            autoSkip: true,
            maxTicksLimit: 8,
          },
          border: { display: false }
        },
        y: { 
          beginAtZero: true,
          grid: { color: '#f0f0f0' },
          ticks: {
            font: { size: 10 },
            color: '#999',
            padding: 6,
          },
          border: {
            display: false,
          }
        } 
      },
      elements: {
        line: {
          capBezierPoints: true,
        }
      }
    }
  });
}

watch(() => [props.labels, props.series], () => build(), { deep: true });
onMounted(() => { build(); });
onBeforeUnmount(() => { if(chartInstance) chartInstance.destroy(); });
</script>
<style scoped>
.chart-wrapper {
  width: 100%;
  position: relative;
  height: var(--chart-height, 200px);
}
</style>
