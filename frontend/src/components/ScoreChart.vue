<template>
  <div class="chart-container">
    <canvas ref="chartRef"></canvas>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { Chart, registerables, type ChartData } from 'chart.js'

Chart.register(...registerables)

const props = defineProps<{
  scorelines: { goals_a: number; goals_b: number; probability: number }[]
}>()

const chartRef = ref<HTMLCanvasElement | null>(null)
let chart: Chart | null = null

function buildChart() {
  if (!chartRef.value || !props.scorelines.length) return
  const ctx = chartRef.value.getContext('2d')!
  if (chart) chart.destroy()

  const top = props.scorelines.slice(0, 8)
  const labels = top.map(s => `${s.goals_a}-${s.goals_b}`)
  const data = top.map(s => s.probability * 100)

  const colors = top.map(s => {
    if (s.goals_a > s.goals_b) return '#a6e3a1'
    if (s.goals_a === s.goals_b) return '#f9e2af'
    return '#f38ba8'
  })

  chart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Probabilidad (%)',
        data,
        backgroundColor: colors,
        borderColor: colors.map(c => c + 'cc'),
        borderWidth: 1,
        borderRadius: 4,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => `${(ctx.parsed.y ?? 0).toFixed(2)}%`,
          },
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { callback: (v) => v + '%', color: '#7a7a9a' },
          grid: { color: '#2a2a4a' },
        },
        x: {
          ticks: { color: '#7a7a9a' },
          grid: { display: false },
        },
      },
    },
  })
}

onMounted(buildChart)
watch(() => props.scorelines, buildChart)
</script>

<style scoped>
.chart-container {
  height: 250px;
  width: 100%;
}
</style>
