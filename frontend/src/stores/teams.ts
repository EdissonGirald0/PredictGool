import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api, type Team, type Group } from '../api/client'

export const useTeamsStore = defineStore('teams', () => {
  const teams = ref<Team[]>([])
  const groups = ref<Group[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const teamsByGroup = computed(() => {
    const map: Record<string, Team[]> = {}
    for (const t of teams.value) {
      if (!map[t.group]) map[t.group] = []
      map[t.group].push(t)
    }
    for (const g of Object.keys(map)) {
      map[g].sort((a, b) => b.elo - a.elo)
    }
    return map
  })

  const topTeams = computed(() =>
    [...teams.value].sort((a, b) => b.elo - a.elo).slice(0, 10)
  )

  async function fetchTeams() {
    loading.value = true
    error.value = null
    try {
      teams.value = await api.get<Team[]>('/teams')
      groups.value = await api.get<Group[]>('/groups')
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  function getTeamById(id: string): Team | undefined {
    return teams.value.find(t => t.id === id)
  }

  return { teams, groups, loading, error, teamsByGroup, topTeams, fetchTeams, getTeamById }
})
