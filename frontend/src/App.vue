<template>
  <div class="app-layout">
    <NavBar />
    <main class="main-content">
      <router-view />
    </main>
    <footer class="app-footer">
      <div class="container footer-content">
        <div class="footer-brand">
          <span class="footer-logo">⚽</span>
          <span class="footer-name">PredictGool</span>
          <span class="footer-version">v1.0</span>
        </div>
        <div class="footer-models">
          Modelos Elo + Dixon-Coles + XGBoost &bull; Monte Carlo &bull; Datos oficiales FIFA 2026
        </div>
        <div class="footer-author">
          <div class="author-card">
            <div class="author-avatar">EG</div>
            <div class="author-info">
              <span class="author-name">Ing. Edisson Giraldo</span>
              <span class="author-title">Data Scientist &amp; Full-Stack Developer</span>
              <div class="author-links">
                <a href="https://github.com/edissongirald0" target="_blank" rel="noopener" class="author-link">
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>
                  edissongirald0
                </a>
                <a href="https://edissongirald0.github.io/" target="_blank" rel="noopener" class="author-link">
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M7.657 0C3.429 0 0 3.429 0 7.657c0 3.384 2.193 6.242 5.23 7.253.38.073.524-.162.524-.36 0-.183-.01-.79-.01-1.434-1.921.361-2.42-.468-2.577-.898-.088-.227-.466-.898-.796-1.08-.272-.146-.661-.505-.011-.514.613-.01 1.051.561 1.196.793.7 1.17 1.821.841 2.265.641.07-.504.274-.842.498-1.035C4.08 10.91 2.28 10.242 2.28 7.3c0-.842.3-1.536.793-2.077-.08-.199-.344-.987.075-2.058 0 0 .646-.203 2.117.793a7.28 7.28 0 011.927-.26c.654 0 1.312.088 1.927.26 1.47-.996 2.117-.793 2.117-.793.42 1.07.156 1.858.076 2.058.493.54.792 1.235.792 2.077 0 2.95-1.802 3.602-3.521 3.795.277.24.524.71.524 1.433 0 1.035-.01 1.869-.01 2.126 0 .2.143.435.524.36 3.033-1.011 5.223-3.87 5.223-7.253C15.314 3.429 11.885 0 7.657 0z"/></svg>
                  edissongirald0.github.io
                </a>
              </div>
            </div>
          </div>
        </div>
        <div class="footer-bottom">
          &copy; 2026 PredictGool &mdash; Todos los derechos reservados
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import NavBar from './components/NavBar.vue'
</script>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
.main-content {
  flex: 1;
  padding: 24px 0 48px;
}
.app-footer {
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-color);
  padding: 32px 0 24px;
  text-align: center;
}
.footer-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}
.footer-brand {
  display: flex;
  align-items: center;
  gap: 8px;
}
.footer-logo { font-size: 1.4rem; }
.footer-name {
  font-size: 1.1rem;
  font-weight: 700;
  background: linear-gradient(135deg, var(--lila), var(--gold));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.footer-version {
  font-size: 0.7rem;
  color: var(--text-muted);
  background: var(--bg-card);
  padding: 2px 8px;
  border-radius: 8px;
}
.footer-models {
  color: var(--text-muted);
  font-size: 0.8rem;
  max-width: 500px;
}
.footer-author {
  margin: 4px 0;
}
.author-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 14px 24px;
  text-align: left;
}
.author-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--gradient-primary);
  color: var(--cream);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.9rem;
  flex-shrink: 0;
}
.author-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.author-name {
  font-weight: 600;
  font-size: 0.95rem;
  color: var(--text-primary);
}
.author-title {
  font-size: 0.78rem;
  color: var(--text-secondary);
}
.author-links {
  display: flex;
  gap: 14px;
  margin-top: 6px;
  flex-wrap: wrap;
}
.author-link {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 0.78rem;
  color: var(--lila);
  transition: color 0.2s;
}
.author-link:hover {
  color: var(--gold);
}
.author-link svg {
  flex-shrink: 0;
}
.footer-bottom {
  font-size: 0.72rem;
  color: var(--text-muted);
  padding-top: 4px;
}
@media (max-width: 480px) {
  .author-card { flex-direction: column; text-align: center; padding: 16px; }
  .author-links { justify-content: center; }
}
</style>
