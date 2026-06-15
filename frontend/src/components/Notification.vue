<template>
  <Teleport to="body">
    <Transition name="notif">
      <div v-if="visible" class="notification" :class="type">
        <span class="notif-icon">{{ icon }}</span>
        <span class="notif-msg">{{ message }}</span>
        <button class="notif-close" @click="close">×</button>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const visible = ref(false)
const message = ref('')
const type = ref<'success' | 'info' | 'warning'>('info')
let timer: ReturnType<typeof setTimeout> | null = null

const iconMap = { success: '✅', info: 'ℹ️', warning: '⚠️' }

const icon = ref(iconMap.info)

function show(msg: string, t: 'success' | 'info' | 'warning' = 'info', duration = 4000) {
  message.value = msg
  type.value = t
  icon.value = iconMap[t]
  visible.value = true
  if (timer) clearTimeout(timer)
  timer = setTimeout(close, duration)
}

function close() {
  visible.value = false
  if (timer) clearTimeout(timer)
}

defineExpose({ show })
</script>

<style scoped>
.notification {
  position: fixed;
  top: 80px;
  right: 20px;
  z-index: 1000;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 20px;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  min-width: 280px;
  max-width: 420px;
  font-size: 0.9rem;
  backdrop-filter: blur(10px);
}
.notification.success { background: rgba(166, 227, 161, 0.15); border: 1px solid var(--win-color); color: var(--win-color); }
.notification.info { background: rgba(196, 174, 244, 0.15); border: 1px solid var(--lila); color: var(--lila); }
.notification.warning { background: rgba(249, 226, 175, 0.15); border: 1px solid var(--draw-color); color: var(--draw-color); }
.notif-icon { font-size: 1.2rem; }
.notif-msg { flex: 1; }
.notif-close {
  background: none;
  border: none;
  color: inherit;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0 4px;
  opacity: 0.6;
}
.notif-close:hover { opacity: 1; }
.notif-enter-active { transition: all 0.3s ease; }
.notif-leave-active { transition: all 0.2s ease; }
.notif-enter-from { transform: translateX(100%); opacity: 0; }
.notif-leave-to { transform: translateX(100%); opacity: 0; }
</style>
