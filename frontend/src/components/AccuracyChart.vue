<template>
  <div class="chart-container">
    <canvas ref="chartRef"></canvas>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

interface ResultRow {
  team_a: string
  team_b: string
  score_a: number
  score_b: number
}

interface DailyAccuracy {
  date: string
  accuracy: number
  total: number
}

const props = defineProps<{
  predictions: { result: ResultRow; predicted_winner: string | null; correct: boolean }[]
  days?: DailyAccuracy[]
}>()

const chartRef = ref<HTMLCanvasElement | null>(null)
let chart: Chart | null = null

const accuracy = computed(() => {
  if (!props.predictions.length) return 0
  const correct = props.predictions.filter(p => p.correct).length
  return (correct / props.predictions.length) * 100
})

function buildChart() {
  if (!chartRef.value) return
  const ctx = chartRef.value.getContext('2d')!
  if (chart) chart.destroy()

  const correct = props.predictions.filter(p => p.correct).length
  const incorrect = props.predictions.length - correct

  chart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Aciertos', 'Fallos'],
      datasets: [{
        data: [correct, incorrect],
        backgroundColor: ['#a6e3a1', '#f38ba8'],
        borderColor: ['#a6e3a1', '#f38ba8'],
        borderWidth: 1,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: { color: '#C4AEF4', padding: 16 },
        },
        tooltip: {
          callbacks: {
            label: (ctx) => {
              const total = correct + incorrect
              const pct = ctx.parsed / (total || 1) * 100
              return `${ctx.label}: ${ctx.parsed} (${pct.toFixed(1)}%)`
            },
          },
        },
      },
    },
  })
}

onMounted(buildChart)
watch(() => props.predictions, buildChart)
</script>

<style scoped>
.chart-container {
  height: 240px;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.accuracy-value {
  position: absolute;
  font-size: 2rem;
  font-weight: 700;
  color: var(--gold);
}
</style>
