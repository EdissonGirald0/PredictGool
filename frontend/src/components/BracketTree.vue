<template>
  <div class="card bracket-tree">
    <h3 class="section-title">Cuadro Eliminatorio</h3>
    <p class="bracket-note">
      El bracket se bloquea tras la fase de grupos. Las posiciones dependen de los resultados de grupo.
    </p>

    <div class="bracket-rounds">
      <div v-for="(stage, stageName) in stages" :key="stageName" class="bracket-stage">
        <h4 class="stage-title">{{ stageName }}</h4>
        <div class="stage-matches">
          <div v-for="m in stage" :key="m.id" class="bracket-match">
            <div class="match-slot" :class="{ 'match-played': m.played }">
              <span class="slot-team">{{ m.team_a || '—' }}</span>
              <span v-if="m.played" class="slot-score">{{ m.score_a }}</span>
            </div>
            <div class="match-divider">vs</div>
            <div class="match-slot" :class="{ 'match-played': m.played }">
              <span class="slot-team">{{ m.team_b || '—' }}</span>
              <span v-if="m.played" class="slot-score">{{ m.score_b }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { api, type Fixture } from '../api/client'
import { ref } from 'vue'

const stages = ref<Record<string, Fixture[]>>({})

async function loadBracket() {
  try {
    const data = await api.get<{ stages: Record<string, Fixture[]> }>('/simulate/bracket')
    stages.value = data.stages
  } catch (e) {
    console.error(e)
  }
}
loadBracket()
</script>

<style scoped>
.bracket-note {
  color: var(--text-muted);
  font-size: 0.85rem;
  margin-bottom: 20px;
}
.bracket-rounds {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  padding-bottom: 12px;
}
.bracket-stage {
  min-width: 140px;
  flex-shrink: 0;
}
.stage-title {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--gold);
  margin-bottom: 12px;
  text-align: center;
}
.stage-matches {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.bracket-match {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  padding: 6px 10px;
  font-size: 0.8rem;
}
.match-slot {
  display: flex;
  justify-content: space-between;
  padding: 3px 0;
}
.match-divider {
  text-align: center;
  color: var(--text-muted);
  font-size: 0.7rem;
  padding: 2px 0;
}
.slot-score {
  font-weight: 700;
  color: var(--gold);
}
.match-played .slot-team {
  color: var(--text-secondary);
}
</style>
