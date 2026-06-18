<template>
  <div class="container">
    <h1 class="page-title">Fase de Grupos</h1>
    <p class="page-subtitle">
      12 grupos de 4 equipos. Clasifican los 2 primeros + 8 mejores terceros.
      <span class="live-badge">EN VIVO</span>
    </p>

    <div v-if="dataStore.loading && !hasData" class="spinner"></div>

    <div v-else-if="dataStore.error" class="card" style="text-align:center;color:var(--loss-color)">
      {{ dataStore.error }}
      <button class="btn btn-outline" style="margin-top:12px" @click="dataStore.refreshAll()">Reintentar</button>
    </div>

    <div v-else class="groups-grid">
      <div v-for="gid in sortedGroupIds" :key="gid" class="group-card card">
        <h3 class="section-title">Grupo {{ gid }}</h3>
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Equipo</th>
              <th>PTS</th>
              <th>PJ</th>
              <th>G</th>
              <th>E</th>
              <th>P</th>
              <th>GF</th>
              <th>GC</th>
              <th>DG</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(row, i) in (standings[gid] || defaultRows(gid))"
              :key="row.team_id || row.team_name"
              :class="{ 'qualified-row': row.position && row.position <= 2, 'third-row': row.position === 3 }"
            >
              <td>{{ row.position || i + 1 }}</td>
              <td class="team-cell">
                <span class="team-emoji">{{ getFlag(row.team_id || row.team_name) }}</span>
                <span>{{ row.team_name }}</span>
              </td>
              <td><strong>{{ row.pts || 0 }}</strong></td>
              <td>{{ row.played || 0 }}</td>
              <td>{{ row.w || 0 }}</td>
              <td>{{ row.d || 0 }}</td>
              <td>{{ row.l || 0 }}</td>
              <td>{{ row.gf || 0 }}</td>
              <td>{{ row.ga || 0 }}</td>
              <td :class="gdClass(row.gd || 0)">{{ formatGD(row.gd || 0) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="bestThirds.length" class="card best-thirds">
        <h3 class="section-title">Ranking de Terceros</h3>
        <p class="third-note">Los 8 mejores terceros avanzan a dieciseisavos</p>
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Equipo</th>
              <th>Grupo</th>
              <th>PTS</th>
              <th>DG</th>
              <th>GF</th>
              <th>Clasifica</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(t, i) in bestThirds" :key="t.team_name" :class="{ 'qualified-row': i < 8 }">
              <td>{{ i + 1 }}</td>
              <td><strong>{{ t.team_name }}</strong></td>
              <td>{{ getGroupForTeam(t.team_name) }}</td>
              <td>{{ t.pts }}</td>
              <td :class="gdClass(t.gd)">{{ formatGD(t.gd) }}</td>
              <td>{{ t.gf }}</td>
              <td>
                <span :class="i < 8 ? 'badge badge-win' : 'badge badge-loss'">
                  {{ i < 8 ? '✓' : '✗' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useDataStore } from '../stores/data'
import { useTeamsStore } from '../stores/teams'

const dataStore = useDataStore()
const teamsStore = useTeamsStore()
const { standings, bestThirds } = storeToRefs(dataStore)

const sortedGroupIds = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']

const hasData = computed(() => Object.keys(standings.value).length > 0)

function getFlag(nameOrId: string): string {
  const team = teamsStore.teams.find(t => t.id === nameOrId || t.name === nameOrId)
  return team?.flag_emoji || '🏳️'
}

function getGroupForTeam(name: string): string {
  return teamsStore.teams.find(t => t.name === name)?.group || '?'
}

function defaultRows(gid: string) {
  const teamNames = teamsStore.teams.filter(t => t.group === gid).map(t => t.name)
  return teamNames.map((name, i) => ({
    team_id: '',
    team_name: name,
    pts: 0, played: 0, w: 0, d: 0, l: 0, gf: 0, ga: 0, gd: 0, position: 0,
  }))
}

function formatGD(gd: number): string {
  return gd > 0 ? `+${gd}` : `${gd}`
}
function gdClass(gd: number): string {
  return gd > 0 ? 'gd-positive' : gd < 0 ? 'gd-negative' : ''
}

onMounted(async () => {
  if (!teamsStore.teams.length) await teamsStore.fetchTeams()
  if (!hasData.value) await dataStore.refreshAll()
})
</script>

<style scoped>
.groups-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}
.group-card { overflow-x: auto; }
.group-card table { min-width: 500px; }
.team-cell { display: flex; align-items: center; gap: 6px; white-space: nowrap; }
.team-emoji { font-size: 1rem; }
.qualified-row td { background: rgba(166, 227, 161, 0.06); }
.third-row td { background: rgba(249, 226, 175, 0.04); }
.gd-positive { color: var(--win-color); font-weight: 600; }
.gd-negative { color: var(--loss-color); }
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
.best-thirds { grid-column: 1 / -1; margin-top: 8px; }
.third-note { color: var(--text-muted); font-size: 0.85rem; margin-bottom: 12px; }
@media (max-width: 900px) {
  .groups-grid { grid-template-columns: 1fr; }
}
</style>
