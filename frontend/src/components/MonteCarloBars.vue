<template>
  <div class="card monte-carlo-card">
    <h3 class="section-title">
      Probabilidad de Campeón
      <span v-if="simCount" class="sim-count">{{ simCount.toLocaleString() }} simulaciones</span>
    </h3>

    <div v-if="loading" class="spinner"></div>

    <div v-else-if="favorites.length" class="bars-container">
      <div
        v-for="(team, i) in favorites"
        :key="team.team_name"
        class="mc-bar"
      >
        <div class="mc-rank">{{ i + 1 }}</div>
        <div class="mc-name">{{ team.team_name }}</div>
        <div class="mc-bar-track">
          <div
            class="mc-bar-fill"
            :class="barClass(i)"
            :style="{ width: (team.probability * 100 / maxProb) + '%' }"
          ></div>
        </div>
        <div class="mc-prob">{{ (team.probability * 100).toFixed(1) }}%</div>
      </div>
    </div>

    <div v-else class="empty-state">
      <p>Ejecuta una simulación para ver las probabilidades</p>
      <button class="btn btn-primary" @click="$emit('simulate')">
        Simular Torneo
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ChampionProb } from '../api/client'

const props = defineProps<{
  favorites: ChampionProb[]
  loading?: boolean
  simCount?: number
}>()

defineEmits<{ simulate: [] }>()

const maxProb = computed(() => {
  if (!props.favorites.length) return 1
  return Math.max(...props.favorites.map(f => f.probability))
})

function barClass(index: number): string {
  if (index === 0) return 'bar-gold'
  if (index === 1) return 'bar-silver'
  if (index === 2) return 'bar-bronze'
  return ''
}
</script>

<style scoped>
.monte-carlo-card { max-width: 600px; margin: 0 auto; }
.sim-count { font-size: 0.8rem; color: var(--text-muted); font-weight: 400; }
.bars-container { display: flex; flex-direction: column; gap: 10px; }
.mc-bar {
  display: flex;
  align-items: center;
  gap: 10px;
}
.mc-rank {
  width: 24px;
  text-align: center;
  font-weight: 700;
  font-size: 0.85rem;
  color: var(--text-muted);
}
.mc-name {
  min-width: 120px;
  font-size: 0.9rem;
  font-weight: 500;
}
.mc-bar-track {
  flex: 1;
  height: 20px;
  background: var(--bg-secondary);
  border-radius: 4px;
  overflow: hidden;
}
.mc-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.6s ease;
  background: var(--lila);
  min-width: 2px;
}
.bar-gold { background: var(--gradient-gold); }
.bar-silver { background: linear-gradient(135deg, #b0b0b0, #d0d0d0); }
.bar-bronze { background: linear-gradient(135deg, #cd7f32, #e0a050); }
.mc-prob {
  min-width: 52px;
  text-align: right;
  font-weight: 600;
  font-size: 0.9rem;
}
.empty-state { text-align: center; padding: 32px 0; }
.empty-state p { color: var(--text-muted); margin-bottom: 16px; }
</style>
