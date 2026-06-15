<template>
  <div class="card live-results">
    <h3 class="section-title">Resultados</h3>

    <div v-if="results.length === 0" class="empty-state">
      <p>Aún no hay resultados registrados</p>
    </div>

    <div v-else class="results-list">
      <div v-for="r in results" :key="r.id" class="result-row">
        <div class="result-date">{{ r.date || '—' }}</div>
        <div class="result-teams">
          <span class="team-name" :class="{ winner: r.score_a > r.score_b }">{{ r.team_a }}</span>
          <span class="result-score">{{ r.score_a }} - {{ r.score_b }}</span>
          <span class="team-name" :class="{ winner: r.score_b > r.score_a }">{{ r.team_b }}</span>
        </div>
        <div class="result-stage">
          <span class="badge badge-lila">{{ r.stage || 'Grupo' }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { MatchResult } from '../api/client'

defineProps<{ results: MatchResult[] }>()
</script>

<style scoped>
.results-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.result-row {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 10px 14px;
  background: var(--bg-secondary);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-color);
}
.result-date {
  font-size: 0.8rem;
  color: var(--text-muted);
  min-width: 80px;
}
.result-teams {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
}
.team-name {
  font-weight: 500;
  flex: 1;
}
.team-name.winner {
  color: var(--win-color);
  font-weight: 600;
}
.team-name:last-child { text-align: right; }
.result-score {
  font-weight: 700;
  font-size: 1.05rem;
  padding: 4px 12px;
  background: var(--bg-card);
  border-radius: 4px;
}
.result-stage { min-width: 60px; text-align: right; }
.empty-state {
  text-align: center;
  padding: 24px;
  color: var(--text-muted);
}
@media (max-width: 768px) {
  .result-row { flex-direction: column; gap: 6px; align-items: flex-start; }
  .result-teams { width: 100%; }
}
</style>
