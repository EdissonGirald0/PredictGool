<template>
  <div class="container">
    <h1 class="page-title">Cuadro Eliminatorio</h1>
    <p class="page-subtitle">
      Bracket bloqueado FIFA 2026 — R32 → Octavos → Cuartos → Semis → Final
      <span class="live-badge">EN VIVO</span>
    </p>

    <div v-if="loading" class="spinner"></div>

    <div v-else-if="error" class="card" style="text-align:center;color:var(--loss-color)">
      {{ error }}
      <button class="btn btn-outline" style="margin-top:12px" @click="fetchBracket">Reintentar</button>
    </div>

    <div v-else>
      <div class="card" style="margin-bottom:20px">
        <h3 class="section-title">
          {{ groupsComplete ? 'Bracket Eliminatorio' : 'Bracket Proyectado (fase de grupos en curso)' }}
        </h3>

        <div class="bracket-scroll">
          <div v-for="(stage, stageName) in orderedStages" :key="stageName" class="bracket-round">
            <h4 class="round-title">{{ stageLabel(stageName) }}</h4>
            <div class="round-matches">
              <div
                v-for="m in stage"
                :key="m.id"
                class="bracket-match"
                :class="{ 'match-live': m.played }"
              >
                <div class="match-teams">
                  <div class="match-team" :class="{ 'team-advances': m.played && m.score_a != null && m.score_b != null && m.score_a > m.score_b }">
                    <span class="team-name">{{ m.team_a }}</span>
                    <span v-if="m.played" class="team-score">{{ m.score_a }}</span>
                  </div>
                  <div class="match-vs">
                    <span v-if="!m.played">vs</span>
                    <span v-else class="score-sep">-</span>
                  </div>
                  <div class="match-team" :class="{ 'team-advances': m.played && m.score_a != null && m.score_b != null && m.score_b > m.score_a }">
                    <span class="team-name">{{ m.team_b }}</span>
                    <span v-if="m.played" class="team-score">{{ m.score_b }}</span>
                  </div>
                </div>
                <div v-if="m.date" class="match-date">{{ m.date }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <h3 class="section-title">32 Clasificados a R32</h3>
        <div class="qualified-grid">
          <div v-for="(team, i) in qualifiedR32" :key="team" class="qualified-item">
            <span class="q-rank">{{ i + 1 }}</span>
            <span class="q-name">{{ team }}</span>
          </div>
          <div v-if="qualifiedR32.length === 0" class="empty-state">
            La fase de grupos aún no ha terminado. Los clasificados se mostrarán aquí.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { api, type CurrentBracket, type BracketStage } from '../api/client'
import { useResultsStore } from '../stores/results'

const resultsStore = useResultsStore()
const bracket = ref<CurrentBracket | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

const STAGE_ORDER = ['Round of 32', 'Round of 16', 'Quarter-finals', 'Semi-finals', 'Third place', 'Final']

const groupsComplete = computed(() => bracket.value?.groups_complete ?? false)
const qualifiedR32 = computed(() => bracket.value?.qualified_r32 ?? [])

function stageLabel(name: string): string {
  const labels: Record<string, string> = {
    'Round of 32': 'R32',
    'Round of 16': 'Octavos',
    'Quarter-finals': 'Cuartos',
    'Semi-finals': 'Semis',
    'Third place': '3er Puesto',
    'Final': 'Final',
  }
  return labels[name] || name
}

const orderedStages = computed(() => {
  if (!bracket.value?.stages) return {}
  const result: Record<string, BracketStage[]> = {}
  for (const name of STAGE_ORDER) {
    if (bracket.value.stages[name]) {
      result[name] = bracket.value.stages[name]
    }
  }
  return result
})

async function fetchBracket() {
  loading.value = true
  error.value = null
  try {
    bracket.value = await api.get<CurrentBracket>('/simulate/bracket/current')
  } catch (e: any) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(fetchBracket)
watch(() => resultsStore.dataVersion, fetchBracket)
</script>

<style scoped>
.bracket-scroll {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding-bottom: 8px;
}
.bracket-round {
  min-width: 150px;
  flex-shrink: 0;
}
.round-title {
  text-align: center;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--gold);
  margin-bottom: 10px;
  padding: 4px 8px;
  background: var(--bg-secondary);
  border-radius: 4px;
}
.round-matches {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.bracket-match {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  padding: 8px 10px;
  font-size: 0.8rem;
}
.match-live {
  border-color: var(--lila);
  background: rgba(196, 174, 244, 0.06);
}
.match-teams {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.match-team {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.team-name {
  color: var(--text-secondary);
}
.team-advances .team-name {
  color: var(--win-color);
  font-weight: 600;
}
.team-score {
  font-weight: 700;
  color: var(--gold);
  margin-left: 8px;
}
.match-vs {
  text-align: center;
  color: var(--text-muted);
  font-size: 0.7rem;
}
.score-sep {
  color: var(--text-muted);
}
.match-date {
  text-align: center;
  font-size: 0.7rem;
  color: var(--text-muted);
  margin-top: 4px;
}
.qualified-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 8px;
}
.qualified-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--bg-secondary);
  border-radius: var(--radius-sm);
}
.q-rank {
  font-weight: 700;
  color: var(--text-muted);
  min-width: 22px;
}
.q-name {
  font-weight: 500;
}
.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 24px;
  color: var(--text-muted);
}
.live-badge {
  background: rgba(243, 139, 168, 0.2);
  color: var(--loss-color);
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  margin-left: 8px;
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}
</style>
