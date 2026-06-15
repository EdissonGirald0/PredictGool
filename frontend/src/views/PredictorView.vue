<template>
  <div class="container">
    <h1 class="page-title">Predicción de Partido</h1>
    <p class="page-subtitle">Selecciona dos equipos para predecir el resultado usando el modelo Dixon-Coles</p>

    <MatchPredictor />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useTeamsStore } from '../stores/teams'
import MatchPredictor from '../components/MatchPredictor.vue'

const store = useTeamsStore()
onMounted(() => {
  if (!store.teams.length) store.fetchTeams()
})
</script>
