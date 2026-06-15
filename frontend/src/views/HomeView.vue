<template>
  <div class="container">
    <div class="hero">
      <h1 class="page-title">PredictGool</h1>
      <p class="page-subtitle">Predicciones basadas en modelos Elo + Dixon-Coles + XGBoost (ensemble) para el Mundial FIFA 2026</p>
      <div class="hero-actions">
        <router-link to="/predict" class="btn btn-gold">Predecir Partido</router-link>
        <button class="btn btn-outline" @click="runSim" :disabled="simStore.loading">
          {{ simStore.loading ? 'Simulando...' : 'Simular Torneo' }}
        </button>
      </div>
    </div>

    <div v-if="error" class="card" style="text-align:center;color:var(--loss-color)">{{ error }}</div>

    <div class="grid grid-2" style="margin-top:32px">
      <MonteCarloBars
        :favorites="favorites"
        :loading="simStore.loading"
        :sim-count="simCount"
        @simulate="runSim"
      />

      <div class="card">
        <h3 class="section-title">Estadísticas del Torneo</h3>
        <div class="stats-grid">
          <div class="stat-item">
            <span class="stat-number">48</span>
            <span class="stat-label">Selecciones</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">104</span>
            <span class="stat-label">Partidos</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">12</span>
            <span class="stat-label">Grupos</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">39</span>
            <span class="stat-label">Días</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">8</span>
            <span class="stat-label">Partidos del Campeón</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">3</span>
            <span class="stat-label">Países Sede</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="favorites.length > 0" class="card" style="margin-top:24px">
      <h3 class="section-title">Probabilidad de Campeón (Monte Carlo)</h3>
      <ChampionChart :favorites="favorites" />
    </div>

    <div class="card" style="margin-top:24px">
      <h3 class="section-title">Top 20 Rankings Elo</h3>
      <EloChart :teams="teamsStore.teams" />
    </div>

    <div class="card" style="margin-top:24px">
      <h3 class="section-title">Top 10 Equipos por Rating Elo</h3>
      <div class="top-elo-grid">
        <div v-for="(t, i) in topByElo" :key="t.id" class="top-elo-item">
          <span class="top-rank">{{ i + 1 }}</span>
          <span class="top-flag">{{ t.flag_emoji }}</span>
          <span class="top-name">{{ t.name }}</span>
          <span class="top-elo">{{ t.elo }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useTeamsStore } from '../stores/teams'
import { useSimulationStore } from '../stores/simulation'
import MonteCarloBars from '../components/MonteCarloBars.vue'
import ChampionChart from '../components/ChampionChart.vue'
import EloChart from '../components/EloChart.vue'

const teamsStore = useTeamsStore()
const simStore = useSimulationStore()

const error = computed(() => teamsStore.error || simStore.error)

const topByElo = computed(() => {
  return [...teamsStore.teams].sort((a, b) => b.elo - a.elo).slice(0, 10)
})

const favorites = computed(() => {
  return simStore.monteCarloResult?.champion_probabilities || []
})

const simCount = computed(() => {
  return simStore.monteCarloResult?.total_simulations || 0
})

async function runSim() {
  await simStore.runSimulation(500)
}

onMounted(async () => {
  await teamsStore.fetchTeams()
})
</script>

<style scoped>
.hero {
  text-align: center;
  padding: 48px 0 20px;
}
.hero-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 24px;
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
.stat-item {
  text-align: center;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: var(--radius-sm);
}
.stat-number {
  display: block;
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--gold);
  line-height: 1.2;
}
.stat-label {
  font-size: 0.8rem;
  color: var(--text-muted);
}
.top-elo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 10px;
}
.top-elo-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: var(--bg-secondary);
  border-radius: var(--radius-sm);
}
.top-rank {
  font-weight: 700;
  color: var(--text-muted);
  min-width: 20px;
}
.top-flag { font-size: 1.3rem; }
.top-name { flex: 1; font-weight: 500; }
.top-elo { font-weight: 600; color: var(--lila); }
</style>
