import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api, type MatchResult } from '../api/client'

export const useResultsStore = defineStore('results', () => {
  const results = ref<MatchResult[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const dataVersion = ref(0)

  const stats = computed(() => ({
    total: results.value.length,
    totalGoals: results.value.reduce((s, r) => s + r.score_a + r.score_b, 0),
    homeWins: results.value.filter(r => r.score_a > r.score_b).length,
    draws: results.value.filter(r => r.score_a === r.score_b).length,
    awayWins: results.value.filter(r => r.score_b > r.score_a).length,
  }))

  function bumpVersion() {
    dataVersion.value++
  }

  async function fetchResults() {
    loading.value = true
    error.value = null
    try {
      results.value = await api.get<MatchResult[]>('/results')
      bumpVersion()
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function addResult(result: Omit<MatchResult, 'id' | 'played'>) {
    loading.value = true
    try {
      await api.post('/results', result)
      await fetchResults()
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  return { results, loading, error, stats, dataVersion, bumpVersion, fetchResults, addResult }
})
