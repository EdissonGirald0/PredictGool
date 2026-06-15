<template>
  <div class="card team-card" @click="$emit('select', team.id)">
    <div class="team-card-flag">{{ team.flag_emoji }}</div>
    <div class="team-card-name">{{ team.name }}</div>
    <div class="team-card-group">Grupo {{ team.group }}</div>
    <div class="team-card-elo">
      <span class="elo-label">Elo</span>
      <span class="elo-value">{{ team.elo }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Team } from '../api/client'

defineProps<{ team: Team }>()
defineEmits<{ select: [id: string] }>()
</script>

<style scoped>
.team-card {
  text-align: center;
  cursor: pointer;
  padding: 16px;
}
.team-card-flag { font-size: 2.2rem; margin-bottom: 8px; }
.team-card-name { font-weight: 600; font-size: 0.9rem; margin-bottom: 4px; }
.team-card-group {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-bottom: 8px;
}
.team-card-elo {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--bg-secondary);
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.8rem;
}
.elo-label { color: var(--text-muted); }
.elo-value { font-weight: 600; color: var(--lila); }
</style>
