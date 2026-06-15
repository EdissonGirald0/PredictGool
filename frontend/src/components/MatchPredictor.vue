<template>
  <div class="card match-predictor">
    <h3 class="section-title">Predicción de Partido</h3>
    <div class="predictor-form">
      <div class="team-select">
        <label>{{ teamA?.flag_emoji || '🏳️' }} Equipo A</label>
        <select v-model="selectedA" @change="predict">
          <option value="">Seleccionar equipo...</option>
          <option v-for="t in teams" :key="t.id" :value="t.id">
            {{ t.flag_emoji }} {{ t.name }} ({{ t.elo }})
          </option>
        </select>
      </div>
      <div class="vs-badge">VS</div>
      <div class="team-select">
        <label>{{ teamB?.flag_emoji || '🏳️' }} Equipo B</label>
        <select v-model="selectedB" @change="predict">
          <option value="">Seleccionar equipo...</option>
          <option v-for="t in teams" :key="t.id" :value="t.id">
            {{ t.flag_emoji }} {{ t.name }} ({{ t.elo }})
          </option>
        </select>
      </div>
    </div>

    <div v-if="result" class="prediction-result">
      <div class="prob-bars">
        <div class="prob-item">
          <div class="prob-label">
            <span>{{ teamA?.name || 'A' }}</span>
            <span class="prob-value">{{ (result.win * 100).toFixed(1) }}%</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill progress-win" :style="{ width: (result.win * 100) + '%' }"></div>
          </div>
        </div>
        <div class="prob-item">
          <div class="prob-label">
            <span>Empate</span>
            <span class="prob-value">{{ (result.draw * 100).toFixed(1) }}%</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill progress-draw" :style="{ width: (result.draw * 100) + '%' }"></div>
          </div>
        </div>
        <div class="prob-item">
          <div class="prob-label">
            <span>{{ teamB?.name || 'B' }}</span>
            <span class="prob-value">{{ (result.loss * 100).toFixed(1) }}%</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill progress-loss" :style="{ width: (result.loss * 100) + '%' }"></div>
          </div>
        </div>
      </div>

      <div class="prediction-details">
        <div class="detail-card">
          <span class="detail-label">Goles esperados</span>
          <span class="detail-value">{{ result.expected_goals_a }} - {{ result.expected_goals_b }}</span>
        </div>
        <div class="detail-card">
          <span class="detail-label">Marcador más probable</span>
          <span class="detail-value">{{ result.most_likely_score }}</span>
        </div>
      </div>

      <div v-if="result.top_scorelines?.length" class="scoreline-table">
        <h4>Distribución de marcadores</h4>
        <ScoreChart :scorelines="result.top_scorelines" />
        <h4 style="margin-top:16px">Top 5 marcadores probables</h4>
        <div v-for="(s, i) in result.top_scorelines.slice(0, 5)" :key="i" class="scoreline-row">
          <span class="scoreline-score">{{ s.goals_a }} - {{ s.goals_b }}</span>
          <div class="progress-bar" style="flex:1;min-width:60px">
            <div class="progress-fill progress-lila" :style="{ width: (s.probability * 100 / maxScoreProb) + '%' }"></div>
          </div>
          <span class="scoreline-prob">{{ (s.probability * 100).toFixed(1) }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { api, type PredictResult } from '../api/client'
import { useTeamsStore } from '../stores/teams'
import ScoreChart from './ScoreChart.vue'

const store = useTeamsStore()
const { teams } = storeToRefs(store)

const selectedA = ref('')
const selectedB = ref('')
const result = ref<PredictResult | null>(null)

const teamA = computed(() => teams.value.find(t => t.id === selectedA.value))
const teamB = computed(() => teams.value.find(t => t.id === selectedB.value))

const maxScoreProb = computed(() => {
  if (!result.value?.top_scorelines?.length) return 1
  return Math.max(...result.value.top_scorelines.slice(0, 5).map(s => s.probability))
})

async function predict() {
  if (!selectedA.value || !selectedB.value || selectedA.value === selectedB.value) {
    result.value = null
    return
  }
  try {
    result.value = await api.post<PredictResult>('/predict', {
      team_a: selectedA.value,
      team_b: selectedB.value,
      detailed: true,
    })
  } catch (e) {
    console.error(e)
  }
}
</script>

<style scoped>
.match-predictor { max-width: 600px; margin: 0 auto; }
.predictor-form {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  margin-bottom: 24px;
}
.team-select { flex: 1; }
.team-select label {
  display: block;
  margin-bottom: 6px;
  color: var(--text-secondary);
  font-size: 0.85rem;
}
.vs-badge {
  padding: 10px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  font-weight: 700;
  color: var(--gold);
  margin-bottom: 0;
}
.prediction-result { margin-top: 24px; }
.prob-bars { margin-bottom: 20px; }
.prob-item { margin-bottom: 12px; }
.prob-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
  font-size: 0.9rem;
}
.prob-value { font-weight: 600; color: var(--text-secondary); }
.prediction-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 20px;
}
.detail-card {
  background: var(--bg-secondary);
  border-radius: var(--radius-sm);
  padding: 14px;
  text-align: center;
}
.detail-label { display: block; font-size: 0.8rem; color: var(--text-muted); margin-bottom: 4px; }
.detail-value { font-size: 1.1rem; font-weight: 600; }
.scoreline-table h4 { margin-bottom: 10px; color: var(--text-secondary); font-size: 0.9rem; }
.scoreline-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}
.scoreline-score {
  font-family: monospace;
  font-size: 0.95rem;
  min-width: 36px;
}
.scoreline-prob {
  font-size: 0.85rem;
  color: var(--text-muted);
  min-width: 48px;
  text-align: right;
}
@media (max-width: 768px) {
  .predictor-form { flex-direction: column; }
  .vs-badge { text-align: center; }
  .prediction-details { grid-template-columns: 1fr; }
}
</style>
