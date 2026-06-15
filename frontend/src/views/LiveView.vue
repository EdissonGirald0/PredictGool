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

    <div style="margin-top:24px">
      <LiveResults :results="results" />
    </div>

    <Notification ref="notif" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { useTeamsStore } from '../stores/teams'
import { useResultsStore } from '../stores/results'
import LiveResults from '../components/LiveResults.vue'
import Notification from '../components/Notification.vue'

const teamsStore = useTeamsStore()
const resultsStore = useResultsStore()
const notif = ref<any>(null)

const { teams } = teamsStore
const { results, stats } = resultsStore

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
  const teamAData = teams.find(t => t.id === newResult.team_a)
  const teamBData = teams.find(t => t.id === newResult.team_b)
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
  notif.value?.show('Resultado registrado. Grupos y Bracket actualizados.', 'success')
}

onMounted(async () => {
  await teamsStore.fetchTeams()
  await resultsStore.fetchResults()
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
</style>
