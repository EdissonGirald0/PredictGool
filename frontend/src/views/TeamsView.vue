<template>
  <div class="container">
    <h1 class="page-title">Las 48 Selecciones</h1>
    <p class="page-subtitle">Ratings Elo, grupos y datos de cada equipo clasificado al Mundial 2026</p>

    <div v-if="loading" class="spinner"></div>

    <div v-else>
      <div class="filters">
        <select v-model="selectedGroup" class="filter-select">
          <option value="">Todos los grupos</option>
          <option v-for="g in groups" :key="g.id" :value="g.id">Grupo {{ g.id }}</option>
        </select>
        <input v-model="searchQuery" type="text" placeholder="Buscar equipo..." class="filter-input" />
      </div>

      <div class="grid grid-4" v-if="filteredTeams.length">
        <TeamCard
          v-for="t in filteredTeams"
          :key="t.id"
          :team="t"
          @select="selectTeam"
        />
      </div>
      <div v-else class="empty-state card">
        <p>No se encontraron equipos</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTeamsStore } from '../stores/teams'
import TeamCard from '../components/TeamCard.vue'

const router = useRouter()
const store = useTeamsStore()
const { teams, groups, loading } = store

const selectedGroup = ref('')
const searchQuery = ref('')

const filteredTeams = computed(() => {
  let list = teams
  if (selectedGroup.value) {
    list = list.filter(t => t.group === selectedGroup.value)
  }
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(t => t.name.toLowerCase().includes(q) || t.id.includes(q))
  }
  return list.sort((a, b) => b.elo - a.elo)
})

function selectTeam(id: string) {
  router.push(`/predict?team=${id}`)
}

onMounted(() => store.fetchTeams())
</script>

<style scoped>
.filters {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}
.filter-select { max-width: 200px; }
.filter-input { max-width: 300px; }
.empty-state { text-align: center; padding: 32px; color: var(--text-muted); }
@media (max-width: 768px) {
  .filters { flex-direction: column; }
  .filter-select, .filter-input { max-width: 100%; }
}
</style>
