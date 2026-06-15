import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api, type MonteCarloResult } from '../api/client'

export const useSimulationStore = defineStore('simulation', () => {
  const monteCarloResult = ref<MonteCarloResult | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function runSimulation(n: number = 1000) {
    loading.value = true
    error.value = null
    try {
      monteCarloResult.value = await api.post<MonteCarloResult>('/simulate/tournament', { n })
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  return { monteCarloResult, loading, error, runSimulation }
})
