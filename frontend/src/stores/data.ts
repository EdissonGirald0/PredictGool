import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api, type StandingRow, type StandingsData, type CurrentBracket } from '../api/client'

export const useDataStore = defineStore('data', () => {
  const standings = ref<Record<string, StandingRow[]>>({})
  const bestThirds = ref<{ team_name: string; pts: number; gd: number; gf: number }[]>([])
  const bracket = ref<CurrentBracket | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function refreshStandings() {
    try {
      const data = await api.get<StandingsData>('/simulate/standings')
      standings.value = data.standings
      bestThirds.value = data.all_thirds_sorted || []
    } catch (e: any) {
      error.value = e.message
    }
  }

  async function refreshBracket() {
    try {
      bracket.value = await api.get<CurrentBracket>('/simulate/bracket/current')
    } catch (e: any) {
      error.value = e.message
    }
  }

  async function refreshAll() {
    loading.value = true
    error.value = null
    try {
      await Promise.all([refreshStandings(), refreshBracket()])
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  return { standings, bestThirds, bracket, loading, error, refreshStandings, refreshBracket, refreshAll }
})
