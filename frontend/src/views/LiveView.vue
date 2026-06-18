<template>
  <div class="container">
    <h1 class="page-title">Resultados en Vivo</h1>
    <p class="page-subtitle">Tracking de resultados reales del Mundial 2026</p>

    <div class="grid grid-2">
      <div class="card">
        <h3 class="section-title">Resumen</h3>
        <div class="stats-grid">
          <div class="stat-item">
            <span class="stat-number">{{ stats.total }}</span>
            <span class="stat-label">Partidos</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{{ stats.totalGoals }}</span>
            <span class="stat-label">Goles</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{{ stats.homeWins }}</span>
            <span class="stat-label">Local</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{{ stats.draws }}</span>
            <span class="stat-label">Empates</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{{ stats.awayWins }}</span>
            <span class="stat-label">Visitante</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{{ (stats.totalGoals / (stats.total || 1)).toFixed(1) }}</span>
            <span class="stat-label">Goles/partido</span>
          </div>
        </div>
      </div>

      <div class="card">
        <h3 class="section-title">Registrar Resultado</h3>
        <div class="add-result-form">
          <select v-model="newResult.team_a" class="form-select">
            <option value="">Equipo A</option>
            <option v-for="t in teams" :key="t.id" :value="t.id">{{ t.flag_emoji }} {{ t.name }}</option>
          </select>
          <div class="score-inputs">
            <input v-model.number="newResult.score_a" type="number" min="0" max="20" placeholder="0" class="score-input" />
            <span class="score-sep">-</span>
            <input v-model.number="newResult.score_b" type="number" min="0" max="20" placeholder="0" class="score-input" />
          </div>
          <select v-model="newResult.team_b" class="form-select">
            <option value="">Equipo B</option>
            <option v-for="t in teams" :key="t.id" :value="t.id">{{ t.flag_emoji }} {{ t.name }}</option>
          </select>
          <button class="btn btn-primary" @click="submitResult" :disabled="!canSubmit">
            Guardar
          </button>
        </div>
      </div>
    </div>

    <div class="card" style="margin-top:20px">
      <h3 class="section-title">
        Automatización
        <span v-if="autoLoading" class="spinner-inline"></span>
      </h3>
      <div class="auto-actions">
        <button class="btn btn-outline" @click="fetchNewResults" :disabled="autoLoading">
          🔄 Actualizar Resultados (scraping)
        </button>
        <button class="btn btn-outline" @click="recalibrateBias" :disabled="autoLoading">
          ⚖️ Recalibrar Sesgo
        </button>
      </div>
      <div v-if="biasStatus" class="bias-info">
        <div class="bias-row">
          <span class="bias-label">Resultados rastreados:</span>
          <span class="bias-value">{{ biasStatus.total_tracked }}</span>
        </div>
        <div class="bias-row">
          <span class="bias-label">Pesos ensemble:</span>
          <span class="bias-value">
            DC={{ (biasStatus.ensemble_weights?.dixon_coles * 100).toFixed(0) }}%
            XGB={{ (biasStatus.ensemble_weights?.xgboost * 100).toFixed(0) }}%
            Elo={{ (biasStatus.ensemble_weights?.elo * 100).toFixed(0) }}%
          </span>
        </div>
        <div class="bias-row">
          <span class="bias-label">Accuracy DC:</span>
          <span class="bias-value">{{ (biasStatus.model_performance?.dixon_coles?.accuracy * 100).toFixed(1) }}%</span>
        </div>
        <div class="bias-row">
          <span class="bias-label">Accuracy Elo:</span>
          <span class="bias-value">{{ (biasStatus.model_performance?.elo?.accuracy * 100).toFixed(1) }}%</span>
        </div>
        <div class="bias-row">
          <span class="bias-label">Equipos con forma:</span>
          <span class="bias-value">{{ biasStatus.teams_with_form }}</span>
        </div>
      </div>
    </div>

    <div style="margin-top:24px">
      <LiveResults :results="results" />
    </div>

    <Notification ref="notif" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { storeToRefs } from 'pinia'
import { useTeamsStore } from '../stores/teams'
import { useResultsStore } from '../stores/results'
import { useDataStore } from '../stores/data'
import { api } from '../api/client'
import LiveResults from '../components/LiveResults.vue'
import Notification from '../components/Notification.vue'

const teamsStore = useTeamsStore()
const resultsStore = useResultsStore()
const dataStore = useDataStore()
const notif = ref<any>(null)

const { teams } = storeToRefs(teamsStore)
const { results, stats } = storeToRefs(resultsStore)

const autoLoading = ref(false)
const biasStatus = ref<any>(null)

const newResult = reactive({
  team_a: '',
  team_b: '',
  score_a: null as number | null,
  score_b: null as number | null,
})

const canSubmit = computed(() =>
  newResult.team_a && newResult.team_b &&
  newResult.team_a !== newResult.team_b &&
  newResult.score_a !== null && newResult.score_b !== null &&
  newResult.score_a >= 0 && newResult.score_b >= 0
)

async function submitResult() {
  if (!canSubmit.value) return
  const teamAData = teams.value.find(t => t.id === newResult.team_a)
  const teamBData = teams.value.find(t => t.id === newResult.team_b)
  await resultsStore.addResult({
    team_a: teamAData?.name || newResult.team_a,
    team_b: teamBData?.name || newResult.team_b,
    score_a: newResult.score_a!,
    score_b: newResult.score_b!,
    stage: 'group',
    group: teamAData?.group || null,
    date: new Date().toISOString().slice(0, 10),
  })
  newResult.team_a = ''
  newResult.team_b = ''
  newResult.score_a = null
  newResult.score_b = null
  notif.value?.show('Resultado registrado. Grupos, Bracket y Sesgo actualizados.', 'success')
  await loadBiasStatus()
  await dataStore.refreshAll()
}

async function fetchNewResults() {
  autoLoading.value = true
  try {
    const resp = await api.post<any>('/admin/fetch-results')
    if (resp.new_results > 0) {
      notif.value?.show(`${resp.new_results} nuevos resultados encontrados. Total: ${resp.total}`, 'success')
      await resultsStore.fetchResults()
      await loadBiasStatus()
      await dataStore.refreshAll()
    } else {
      notif.value?.show(resp.message || 'No hay resultados nuevos', 'warning')
    }
  } catch (e: any) {
    notif.value?.show('Error al buscar resultados: ' + (e.message || 'Desconocido'), 'warning')
  } finally {
    autoLoading.value = false
  }
}

async function recalibrateBias() {
  autoLoading.value = true
  try {
    const resp = await api.post<any>('/admin/recalibrate')
    notif.value?.show(`Sesgo recalibrado con ${resp.total_tracked} resultados`, 'success')
    await loadBiasStatus()
  } catch (e: any) {
    notif.value?.show('Error al recalibrar: ' + (e.message || 'Desconocido'), 'warning')
  } finally {
    autoLoading.value = false
  }
}

async function loadBiasStatus() {
  try {
    biasStatus.value = await api.get<any>('/admin/bias-status')
  } catch (e) {
    console.error(e)
  }
}

onMounted(async () => {
  await teamsStore.fetchTeams()
  await resultsStore.fetchResults()
  await loadBiasStatus()
})
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}
.stat-item { text-align: center; padding: 12px; background: var(--bg-secondary); border-radius: var(--radius-sm); }
.stat-number { display: block; font-size: 1.5rem; font-weight: 700; color: var(--gold); }
.stat-label { font-size: 0.75rem; color: var(--text-muted); }
.add-result-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.score-inputs {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
}
.score-input {
  width: 60px;
  text-align: center;
  font-size: 1.2rem;
}
.score-sep { font-size: 1.2rem; font-weight: 700; color: var(--text-muted); }
.form-select { width: 100%; }
.auto-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.spinner-inline {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid var(--border-color);
  border-top-color: var(--lila);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  vertical-align: middle;
  margin-left: 8px;
}
@keyframes spin { to { transform: rotate(360deg); } }
.bias-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
  background: var(--bg-secondary);
  border-radius: var(--radius-sm);
  padding: 14px 18px;
}
.bias-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
}
.bias-label {
  color: var(--text-muted);
}
.bias-value {
  font-weight: 600;
  color: var(--lila);
}
</style>
