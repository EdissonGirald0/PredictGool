<template>
  <div class="container">
    <h1 class="page-title">Accuracy Dashboard</h1>
    <p class="page-subtitle">Comparativa de predicciones vs resultados reales registrados</p>

    <div v-if="loading" class="spinner"></div>

    <div v-else-if="data">
      <div class="grid grid-3" style="margin-bottom:24px">
        <div class="card stat-card">
          <span class="stat-label">Total Partidos</span>
          <span class="stat-number">{{ data.total }}</span>
        </div>
        <div class="card stat-card">
          <span class="stat-label">Aciertos</span>
          <span class="stat-number win">{{ data.correct }}</span>
        </div>
        <div class="card stat-card">
          <span class="stat-label">Precisión Global</span>
          <span class="stat-number" :class="accuracyClass">{{ accuracyPercent }}%</span>
        </div>
      </div>

      <div class="grid grid-3" style="margin-bottom:24px">
        <div class="card stat-card" v-for="(info, type) in data.by_result_type" :key="type">
          <span class="stat-label">{{ type === 'win' ? 'Victorias' : type === 'draw' ? 'Empates' : 'Derrotas' }}</span>
          <span class="stat-number">{{ info.total }} partidos</span>
          <span class="stat-sub">{{ info.accuracy ? (info.accuracy * 100).toFixed(1) + '% precisión' : '—' }}</span>
        </div>
      </div>

      <div class="card" style="margin-bottom:24px">
        <h3 class="section-title">Distribución de Aciertos</h3>
        <AccuracyChart :predictions="chartPredictions" />
      </div>

      <div class="card">
        <h3 class="section-title">Detalle por Partido</h3>
        <table>
          <thead>
            <tr>
              <th>Partido</th>
              <th>Resultado</th>
              <th>Predicción</th>
              <th>Acierto</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in data.comparisons" :key="c.team_a + c.team_b">
              <td>{{ c.team_a }} vs {{ c.team_b }}</td>
              <td><strong>{{ c.score_a }} - {{ c.score_b }}</strong></td>
              <td>
                {{ c.predicted_result === 'win' ? 'Victoria' : c.predicted_result === 'draw' ? 'Empate' : 'Derrota' }}
                <span class="pred-probs">
                  ({{ (c.predicted_probabilities.win * 100).toFixed(0) }}% / {{ (c.predicted_probabilities.draw * 100).toFixed(0) }}% / {{ (c.predicted_probabilities.loss * 100).toFixed(0) }}%)
                </span>
              </td>
              <td>
                <span :class="c.correct ? 'badge badge-win' : 'badge badge-loss'">
                  {{ c.correct ? '✓' : '✗' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-else class="card" style="text-align:center;padding:48px">
      <p class="text-muted">No hay resultados registrados para comparar.</p>
      <router-link to="/live" class="btn btn-primary" style="margin-top:16px">Registrar Resultados</router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { api } from '../api/client'
import AccuracyChart from '../components/AccuracyChart.vue'

interface Comparison {
  team_a: string
  team_b: string
  score_a: number
  score_b: number
  actual_result: string
  predicted_result: string
  predicted_probabilities: { win: number; draw: number; loss: number }
  correct: boolean
}

interface AccuracyData {
  total: number
  correct: number
  accuracy: number | null
  comparisons: Comparison[]
  by_result_type: Record<string, { accuracy: number | null; correct: number; total: number }>
}

const data = ref<AccuracyData | null>(null)
const loading = ref(true)

const accuracyPercent = computed(() => {
  if (!data.value?.accuracy) return '0.0'
  return (data.value.accuracy * 100).toFixed(1)
})

const accuracyClass = computed(() => {
  const pct = parseFloat(accuracyPercent.value)
  if (pct >= 60) return 'win'
  if (pct >= 40) return 'draw-color'
  return 'loss'
})

const chartPredictions = computed(() => {
  if (!data.value) return []
  return data.value.comparisons.map(c => ({
    result: {
      team_a: c.team_a,
      team_b: c.team_b,
      score_a: c.score_a,
      score_b: c.score_b,
    },
    predicted_winner: c.predicted_result,
    correct: c.correct,
  }))
})

onMounted(async () => {
  await loadAccuracy()
})

async function loadAccuracy() {
  try {
    const resp = await api.get<AccuracyData>('/accuracy')
    if (resp.total > 0) data.value = resp
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.stat-card {
  text-align: center;
  padding: 24px;
}
.stat-label {
  display: block;
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-bottom: 8px;
}
.stat-number {
  font-size: 2rem;
  font-weight: 700;
}
.stat-number.win { color: var(--win-color); }
.stat-number.loss { color: var(--loss-color); }
.stat-sub {
  display: block;
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-top: 4px;
}
.draw-color { color: var(--draw-color); }
.pred-probs {
  display: block;
  font-size: 0.75rem;
  color: var(--text-muted);
}
.text-muted { color: var(--text-muted); }
</style>
