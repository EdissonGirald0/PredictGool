<template>
  <div class="chart-container">
    <canvas ref="chartRef"></canvas>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

interface Favorite {
  team_name: string
  probability: number
}

const props = defineProps<{
  favorites: Favorite[]
}>()

const chartRef = ref<HTMLCanvasElement | null>(null)
let chart: Chart | null = null

function buildChart() {
  if (!chartRef.value || !props.favorites.length) return
  const ctx = chartRef.value.getContext('2d')!
  if (chart) chart.destroy()

  const top = [...props.favorites].sort((a, b) => b.probability - a.probability).slice(0, 16)
  const labels = top.map(f => f.team_name)
  const data = top.map(f => f.probability * 100)

  const colors = top.map((_, i) => {
    if (i === 0) return '#DCCE40'
    if (i === 1) return '#b0b0b0'
    if (i === 2) return '#cd7f32'
    return '#C4AEF4'
  })

  chart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: '% Campeón',
        data,
        backgroundColor: colors.map(c => c + '88'),
        borderColor: colors,
        borderWidth: 2,
        borderRadius: 4,
      }],
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => `${(ctx.parsed.x ?? 0).toFixed(2)}%`,
          },
        },
      },
      scales: {
        x: {
          beginAtZero: true,
          ticks: { callback: (v) => v + '%', color: '#7a7a9a' },
          grid: { color: '#2a2a4a' },
        },
        y: {
          ticks: { color: '#7a7a9a', font: { size: 12 } },
          grid: { display: false },
        },
      },
    },
  })
}

onMounted(buildChart)
watch(() => props.favorites, buildChart)
</script>

<style scoped>
.chart-container {
  height: 400px;
  width: 100%;
}
</style>
