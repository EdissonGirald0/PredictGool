<template>
  <button class="theme-toggle" @click="toggle" :title="isDark ? 'Modo claro' : 'Modo oscuro'">
    {{ isDark ? '☀️' : '🌙' }}
  </button>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'

const isDark = ref(true)

function toggle() {
  isDark.value = !isDark.value
  apply()
}

function apply() {
  const root = document.documentElement
  if (isDark.value) {
    root.setAttribute('data-theme', 'dark')
    root.style.setProperty('--bg-primary', '#0a0a14')
    root.style.setProperty('--bg-secondary', '#13132a')
    root.style.setProperty('--bg-card', '#1a1a35')
    root.style.setProperty('--bg-card-hover', '#222244')
    root.style.setProperty('--text-primary', '#F5F0FF')
    root.style.setProperty('--text-secondary', '#C4AEF4')
    root.style.setProperty('--text-muted', '#7a7a9a')
    root.style.setProperty('--border-color', '#2a2a4a')
  } else {
    root.setAttribute('data-theme', 'light')
    root.style.setProperty('--bg-primary', '#F5F0FF')
    root.style.setProperty('--bg-secondary', '#ffffff')
    root.style.setProperty('--bg-card', '#ffffff')
    root.style.setProperty('--bg-card-hover', '#f0ebff')
    root.style.setProperty('--text-primary', '#1a1a35')
    root.style.setProperty('--text-secondary', '#472F5B')
    root.style.setProperty('--text-muted', '#6a6a8a')
    root.style.setProperty('--border-color', '#d4cce8')
  }
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

onMounted(() => {
  const saved = localStorage.getItem('theme')
  if (saved === 'light') {
    isDark.value = false
  }
  apply()
})
</script>

<style scoped>
.theme-toggle {
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 50%;
  width: 36px;
  height: 36px;
  font-size: 1.1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}
.theme-toggle:hover {
  background: var(--bg-card-hover);
  transform: scale(1.1);
}
</style>
