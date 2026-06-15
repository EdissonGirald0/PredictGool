<template>
  <nav class="navbar">
    <div class="container nav-inner">
      <router-link to="/" class="nav-brand">
        ⚽ PredictGool
      </router-link>
      <div class="nav-links">
        <router-link to="/" class="nav-link" exact-active-class="active">Inicio</router-link>
        <router-link to="/predict" class="nav-link" active-class="active">Predecir</router-link>
        <router-link to="/groups" class="nav-link" active-class="active">Grupos</router-link>
        <router-link to="/bracket" class="nav-link" active-class="active">Bracket</router-link>
        <router-link to="/teams" class="nav-link" active-class="active">Equipos</router-link>
        <router-link to="/live" class="nav-link" active-class="active">En Vivo</router-link>
        <router-link to="/accuracy" class="nav-link" active-class="active">Accuracy</router-link>
        <ThemeToggle />
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import ThemeToggle from './ThemeToggle.vue'
</script>

<style scoped>
.navbar {
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(10px);
}
.nav-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
}
.nav-brand {
  font-size: 1.3rem;
  font-weight: 700;
  background: linear-gradient(135deg, var(--lila), var(--gold));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.nav-links {
  display: flex;
  align-items: center;
  gap: 4px;
}
.nav-link {
  padding: 8px 16px;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-weight: 500;
  font-size: 0.9rem;
  transition: all 0.2s;
}
.nav-link:hover {
  color: var(--cream);
  background: rgba(196, 174, 244, 0.1);
}
.nav-link.active {
  color: var(--cream);
  background: rgba(196, 174, 244, 0.15);
}
@media (max-width: 768px) {
  .nav-inner { flex-direction: column; height: auto; padding: 12px 0; gap: 8px; }
  .nav-links { flex-wrap: wrap; justify-content: center; }
  .nav-link { padding: 6px 12px; font-size: 0.8rem; }
}
</style>
