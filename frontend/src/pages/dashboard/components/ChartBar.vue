<template>
  <div class="chart-wrapper"><canvas ref="canvas"></canvas></div>
</template>
<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue';
import { Chart } from 'chart.js/auto';

const props = defineProps({ 
  labels: { type: Array, default: () => [] }, 
  values: { type: Array, default: () => [] }, 
  colors: { type: Array, default: () => [] }, 
  height: { type: Number, default: 200 }, 
  title: String, 
  xTitle: { type: String, default: '' }, 
  yTitle: { type: String, default: '' } 
});

const canvas = ref(null);
let chartInstance = null;

// 朴素的纯色调色板
const defaultColors = [
  '#5b8db8',
  '#7ab89d', 
  '#e0a86a',
  '#c47a7a',
  '#9b8ec4',
  '#d4a5b9',
  '#6ab0b0',
  '#b8c26c',
];

function build(){
  if(!canvas.value) return;
  
  const backgroundColors = props.colors.length 
    ? props.colors 
    : props.labels.map((_, i) => defaultColors[i % defaultColors.length]);
  
  if(chartInstance) chartInstance.destroy();
  
  chartInstance = new Chart(canvas.value.getContext('2d'), {
    type: 'bar',
    data: { 
      labels: props.labels, 
      datasets: [{ 
        data: props.values, 
        backgroundColor: backgroundColors,
        borderRadius: 3,
        barPercentage: 0.7,
        categoryPercentage: 0.8,
      }] 
    },
    options: { 
      responsive: true, 
      maintainAspectRatio: false,
      plugins: { 
        legend: { display: false }, 
        title: { 
          display: !!props.title, 
          text: props.title,
          font: { size: 13 },
          color: '#333',
          padding: { bottom: 12 }
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
          displayColors: false,
        }
      }, 
      scales: { 
        y: { 
          beginAtZero: true, 
          grid: { color: '#f0f0f0' },
          ticks: {
            font: { size: 10 },
            color: '#999',
            padding: 6,
          },
          border: { display: false },
          title: { 
            display: !!props.yTitle, 
            text: props.yTitle,
            font: { size: 10 },
            color: '#888',
          } 
        }, 
        x: { 
          grid: { display: false },
          ticks: {
            font: { size: 10 },
            color: '#666',
          },
          border: { display: false },
          title: { 
            display: !!props.xTitle, 
            text: props.xTitle,
            font: { size: 10 },
            color: '#888',
          } 
        } 
      },
      layout: {
        padding: {
          top: 8,
          bottom: 4,
        }
      }
    }
  });
}

watch(() => [props.labels, props.values], () => build(), { deep: true });
onMounted(build);
onBeforeUnmount(() => { if(chartInstance) chartInstance.destroy(); });
</script>
<style scoped>
.chart-wrapper {
  width: 100%;
  height: var(--chart-height, 200px);
}
</style>
