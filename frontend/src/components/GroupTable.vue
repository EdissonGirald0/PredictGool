<template>
  <div class="card group-table">
    <h3 class="section-title">
      Grupo {{ group.id }}
      <span class="group-badge">{{ group.name }}</span>
    </h3>
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
        <tr v-for="(row, i) in sortedTeams" :key="row.id" :class="{ 'qualified-row': i < 2, 'third-row': i === 2 }">
          <td>{{ i + 1 }}</td>
          <td class="team-cell">
            <span class="team-flag">{{ row.flag_emoji }}</span>
            <span>{{ row.name }}</span>
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
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface GroupTeam {
  id: string
  name: string
  flag_emoji: string
  elo: number
  pts?: number
  played?: number
  w?: number
  d?: number
  l?: number
  gf?: number
  ga?: number
  gd?: number
}

const props = defineProps<{
  group: { id: string; name: string; teams: GroupTeam[] }
}>()

const sortedTeams = computed(() => {
  const list = [...props.group.teams]
  list.sort((a, b) => {
    const ptsA = a.pts || 0, ptsB = b.pts || 0
    if (ptsB !== ptsA) return ptsB - ptsA
    const gdA = a.gd || 0, gdB = b.gd || 0
    if (gdB !== gdA) return gdB - gdA
    const gfA = a.gf || 0, gfB = b.gf || 0
    return gfB - gfA
  })
  return list
})

function formatGD(gd: number): string {
  return gd > 0 ? `+${gd}` : `${gd}`
}
function gdClass(gd: number): string {
  return gd > 0 ? 'gd-positive' : gd < 0 ? 'gd-negative' : ''
}
</script>

<style scoped>
.group-table { margin-bottom: 20px; }
.group-badge {
  font-size: 0.8rem;
  color: var(--text-muted);
  font-weight: 400;
}
.team-cell { display: flex; align-items: center; gap: 8px; }
.team-flag { font-size: 1.2rem; }
.qualified-row td { background: rgba(166, 227, 161, 0.04); }
.third-row td { background: rgba(249, 226, 175, 0.04); }
.gd-positive { color: var(--win-color); font-weight: 600; }
.gd-negative { color: var(--loss-color); }
</style>
