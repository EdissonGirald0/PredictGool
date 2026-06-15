<template>
  <div class="chart-container">
    <canvas ref="chartRef"></canvas>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

interface TeamElo {
  id: string
  name: string
  elo: number
  flag_emoji: string
  group: string
}

const props = defineProps<{
  teams: TeamElo[]
}>()

const chartRef = ref<HTMLCanvasElement | null>(null)
let chart: Chart | null = null

function buildChart() {
  if (!chartRef.value || !props.teams.length) return
  const ctx = chartRef.value.getContext('2d')!
  if (chart) chart.destroy()

  const sorted = [...props.teams].sort((a, b) => b.elo - a.elo).slice(0, 20)
  const labels = sorted.map(t => t.flag_emoji + ' ' + t.name)
  const data = sorted.map(t => t.elo)

  const minElo = sorted[sorted.length - 1]?.elo || 1700
  const maxElo = sorted[0]?.elo || 2200

  const colors = sorted.map(t => {
    const pct = (t.elo - minElo) / (maxElo - minElo || 1)
    const r = Math.round(52 + pct * (196 - 52))
    const g = Math.round(28 + pct * (174 - 28))
    const b = Math.round(103 + pct * (244 - 103))
    return `rgba(${r},${g},${b},0.8)`
  })

  chart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Rating Elo',
        data,
        backgroundColor: colors,
        borderColor: colors,
        borderWidth: 1,
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
            label: (ctx) => `Elo: ${ctx.parsed.x}`,
          },
        },
      },
      scales: {
        x: {
          beginAtZero: false,
          min: minElo - 20,
          ticks: { color: '#7a7a9a' },
          grid: { color: '#2a2a4a' },
        },
        y: {
          ticks: { color: '#7a7a9a', font: { size: 11 } },
          grid: { display: false },
        },
      },
    },
  })
}

onMounted(buildChart)
watch(() => props.teams, buildChart)
</script>

<style scoped>
.chart-container {
  height: 500px;
  width: 100%;
}
</style>
