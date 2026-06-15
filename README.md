# PredictGool ⚽

Plataforma de predicciones para la Copa Mundial FIFA 2026 basada en modelos estadísticos Elo + Dixon-Coles + XGBoost (ensemble) + Monte Carlo. Datos oficiales de los 48 equipos con sus 12 grupos reales y resultados de partidos ya jugados.

---

## Autor

**Edisson Giraldo**

- GitHub: [edissongirald0](https://github.com/edissongirald0)
- Sitio: [edissongirald0.github.io](https://edissongirald0.github.io/)

---

## Arquitectura

```
PredictGool/
├── backend/                         # API FastAPI (Python 3.13)
│   ├── main.py                      # App principal + CORS + lifespan + static files
│   ├── config.py                    # Configuración (Elo K-factors, Monte Carlo)
│   ├── requirements.txt             # Dependencias Python
│   ├── apply_real_data.py           # Script que aplica datos oficiales FIFA 2026
│   ├── run_scrapers.py              # Pipeline de datos (usa apply_real_data.py)
│   ├── models/
│   │   ├── elo.py                   # Sistema de rating Elo con K-factor variable
│   │   ├── dixon_coles.py           # Poisson bivariado + corrección τ(x,y)
│   │   ├── tournament.py            # Simulador de torneo + Monte Carlo
│   │   ├── ensemble.py              # Ensemble: Elo + Dixon-Coles + XGBoost
│   │   ├── standings.py             # Posiciones reales desde resultados registrados
│   │   ├── train_xgboost.py         # Entrenador XGBoost (~7,000 partidos)
│   │   └── generate_dataset.py      # Generador de datos sintéticos históricos
│   ├── api/
│   │   ├── predict.py               # POST /api/predict (ensemble)
│   │   ├── teams.py                 # GET /api/teams, /api/groups, /api/fixtures, /api/elo
│   │   ├── simulation.py            # Monte Carlo, standings, bracket actual
│   │   ├── results.py               # GET/POST /api/results (tracking en vivo)
│   │   ├── accuracy.py              # GET /api/accuracy (dashboard de precisión)
│   │   ├── auth.py                  # JWT login/logout/check
│   │   └── admin.py                 # Health, update-elo, reload
│   ├── scrapers/
│   │   ├── scrape_teams.py          # Wikipedia: equipos + grupos (con fallback)
│   │   ├── scrape_fixtures.py       # Generación de calendario (104 partidos)
│   │   ├── scrape_eloratings.py     # eloratings.net: ratings Elo
│   │   ├── scrape_results.py        # Resultados de partidos jugados
│   │   └── scrape_fifa.py           # FIFA.com (datos oficiales)
│   ├── data/                        # JSON estáticos + modelos entrenados
│   │   ├── teams.json               # 48 equipos oficiales
│   │   ├── groups.json              # 12 grupos reales
│   │   ├── fixtures.json            # 104 partidos
│   │   ├── elo_ratings.json         # Ratings Elo actualizados
│   │   ├── results.json             # Resultados reales registrados
│   │   ├── historical_matches.json  # ~7,000 partidos de backtest
│   │   └── models/                  # Modelos XGBoost serializados (.pkl)
│   └── utils/data_loader.py         # load_json / save_json
├── frontend/                        # Vue 3 + Vite + TypeScript
│   ├── src/
│   │   ├── components/              # NavBar, MatchPredictor, ScoreChart,
│   │   │                            # GroupTable, BracketTree, TeamCard,
│   │   │                            # MonteCarloBars, ChampionChart,
│   │   │                            # EloChart, LiveResults, ThemeToggle,
│   │   │                            # Notification, AccuracyChart
│   │   ├── views/                   # Home, Predictor, Groups, Bracket,
│   │   │                            # Teams, Live, Accuracy
│   │   ├── stores/                  # Pinia: teams, results, simulation
│   │   ├── api/client.ts           # Fetch wrapper tipado
│   │   ├── router/index.ts         # Vue Router (hash mode)
│   │   └── style.css               # Tema Amethyst Dawn Haze + dark/light
│   └── dist/                       # Build de producción
├── Dockerfile                       # Despliegue Railway
├── run_scrapers.sh                  # Pipeline de datos
├── start.sh                         # Inicio de desarrollo
└── README.md
```

---

## Stack Tecnológico

| Capa | Tecnología | Versión |
|------|-----------|---------|
| Backend | FastAPI + Uvicorn | Python 3.13 |
| Machine Learning | XGBoost, scikit-learn, NumPy, SciPy | — |
| Scraping | httpx, BeautifulSoup4, lxml | — |
| Auth | JWT + bcrypt | — |
| Frontend | Vue 3 + Vite | TypeScript 5.7 |
| Estado | Pinia | 2.3 |
| Router | Vue Router | 4.5 |
| Gráficos | Chart.js + vue-chartjs | 4.x |
| Tema | Amethyst Dawn Haze (CSS custom properties) | Dark/Light toggle |

---

## Modelos Predictivos

### 1. Sistema Elo (Motor Base)
Variable de mayor peso predictivo (2 órdenes de magnitud sobre otras métricas).

- **K-factor variable:** World Cup=60, Qualifiers=40, Continental=30, Friendly=20
- **Home advantage:** +100 Elo
- **Goal difference multiplier:** `K_adj = K * sqrt(1 + |gd|)`
- `P(win) = 1 / (1 + 10^(-ΔElo/400))`

### 2. Dixon-Coles Poisson
Poisson bivariado con corrección de dependencia para empates cortos (0-0, 1-1).

- `λ_a = exp(μ + att_a + def_b)`, `λ_b = exp(μ + att_b + def_a)`
- Corrección `τ(x,y)` ajusta probabilidad de marcadores ≤1 gol
- RPS validado: 0.162 (línea base 0.245)
- Parámetros ataque/defensa desde Elo normalizado

### 3. XGBoost
Algoritmo de boosting entrenado con ~7,000 partidos sintéticos con distribución Elo realista.

- 5 modelos: win/draw/away (clasificación) + goals_home/goals_away (regresión)
- Accuracy 55.3%, RPS 0.2055, RMSE goles 1.606
- Features: elo_diff, elo_sum, home_advantage, match_type, form_index, defensive_strength

### 4. Ensemble
Combinación ponderada de los 3 modelos:

| Modelo | Peso | Especialidad |
|--------|------|-------------|
| Dixon-Coles | 50% | Marcadores exactos y empates cortos |
| XGBoost | 30% | Patrones no lineales, features estructuradas |
| Elo | 20% | Tendencia general, menor varianza |

### 5. Monte Carlo (Simulación del Torneo)
N simulaciones completas usando Dixon-Coles rápido (17ms/sim). Cada simulación:
1. Simula fase de grupos con tiebreakers FIFA Art. 11.5
2. Simula bracket eliminatorio bloqueado (R32 → Final)
3. Agrega frecuencias: % campeón, % finalista, % semifinalista, % avance de grupo

---

## Endpoints API

### Predicción
| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/predict` | Predicción ensemble `{team_a, team_b, detailed?}` |
| `POST` | `/api/predict/simulate` | Simulación Monte Carlo de un partido |

### Datos
| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/teams` | 48 equipos con nombre, grupo, Elo, bandera |
| `GET` | `/api/teams/{id}` | Perfil de un equipo |
| `GET` | `/api/groups` | 12 grupos con sus 4 equipos |
| `GET` | `/api/fixtures` | Calendario completo (104 partidos) |
| `GET` | `/api/elo` | Rankings Elo ordenados |
| `GET` | `/api/favorites` | Top favoritos con % de campeón |

### Simulación y Standings
| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/simulate/tournament` | Monte Carlo del torneo `{n}` |
| `GET` | `/api/simulate/group/{id}` | Simula un grupo específico |
| `GET` | `/api/simulate/bracket` | Estructura vacía del bracket |
| `GET` | `/api/simulate/standings` | **Posiciones reales** desde resultados registrados |
| `GET` | `/api/simulate/bracket/current` | **Bracket poblado** con los 32 clasificados reales |

### Tracking en Vivo
| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/results` | Resultados registrados |
| `GET` | `/api/results/stats` | Estadísticas (goles, victorias, empates) |
| `POST` | `/api/results` | Registrar resultado → actualiza Elo + standings |

### Accuracy y Admin
| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/accuracy` | Comparativa predicciones vs resultados reales |
| `GET` | `/api/admin/health` | Estado del sistema |
| `POST` | `/api/admin/update-elo` | Recalcular Elo desde resultados |
| `POST` | `/api/admin/reload` | Re-ejecutar pipeline de datos |

### Autenticación
| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/auth/login` | Login JWT (cookie httponly) |
| `POST` | `/api/auth/logout` | Cerrar sesión |
| `GET` | `/api/auth/check` | Verificar sesión |
| `GET` | `/api/auth/me` | Datos del usuario autenticado |

---

## Vistas del Frontend

| Ruta | Vista | Descripción |
|------|-------|-------------|
| `#/` | Home | Dashboard con top favoritos, gráficos Elo, simulación Monte Carlo |
| `#/predict` | Predictor | Selección de 2 equipos + probabilidades ensemble + distribución de marcadores (Chart.js) |
| `#/groups` | Grupos | **Posiciones reales** (PTS/PJ/GF/GC/DG) + ranking de terceros con clasificación |
| `#/bracket` | Bracket | **Bracket poblado** con 32 clasificados reales, R32 → Final |
| `#/teams` | Equipos | Grid filtrable de 48 selecciones con Elo y banderas |
| `#/live` | En Vivo | Registro de resultados + estadísticas + actualización de grupos/bracket |
| `#/accuracy` | Accuracy | Dashboard de precisión: aciertos/fallos, donut chart, detalle por partido |

---

## Tema Visual

Paleta Amethyst Dawn Haze:

| Color | Hex | Uso |
|-------|-----|-----|
| Deep Amethyst | `#341C67` | Gradiente primario |
| Amethyst | `#472F5B` | Gradiente secundario |
| Lila | `#C4AEF4` | Textos secundarios, acentos |
| Mauve | `#CCA4B4` | Decorativo |
| Gold | `#DCCE40` | Destacados, gradiente de campeón |
| Cream | `#F5F0FF` | Texto principal (modo oscuro) |

Soporta toggle **dark/light mode** con persistencia en localStorage.

---

## Datos del Torneo

**Datos oficiales FIFA 2026** extraídos de Wikipedia:

- **48 equipos** en sus **12 grupos reales** (A-L)
- **12 resultados** ya jugados (11-14 Jun 2026): México 2-0 Sudáfrica, Alemania 7-1 Curaçao, Suecia 5-1 Túnez, etc.
- **Ratings Elo** realistas actualizados con cada resultado
- **104 fixtures**: 72 fase de grupos + 32 eliminatorias
- Fechas oficiales: 11 Jun — 19 Jul 2026

### Pipeline de actualización:
```bash
./run_scrapers.sh              # Aplica datos oficiales FIFA 2026
curl -X POST .../api/admin/reload  # Vía API
```

---

## Cómo Ejecutar

### Requisitos
- Python 3.13+
- Node.js 22+
- npm 11+

### Desarrollo

```bash
cd PredictGool

# 1. Crear venv e instalar dependencias
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# 2. Poblar datos oficiales
./run_scrapers.sh

# 3. Instalar frontend
cd frontend && npm install && cd ..

# 4. Iniciar
./start.sh
```

- **Backend:** http://localhost:8000
- **Frontend:** http://localhost:5173
- **API Docs:** http://localhost:8000/docs

### Build de Producción

```bash
cd frontend && npm run build
# El backend sirve frontend/dist/ automáticamente si existe
```

---

## Flujo de Datos en Vivo

```
POST /api/results (registrar resultado)
  → Guarda en results.json
  → Actualiza ratings Elo
  → Frontend notifica "Grupos y Bracket actualizados"

GET /api/simulate/standings
  → Lee results.json + groups.json
  → Calcula PTS, GD, GF reales por grupo
  → Ordena según criterios FIFA Art. 11.5
  → Determina 8 mejores terceros
  → Devuelve 32 clasificados a R32

GET /api/simulate/bracket/current
  → Usa los 32 clasificados reales
  → Puebla el bracket R32 con los equipos
  → Indica si la fase de grupos está completa
```

---

## Roadmap

### Fase 1 (MVP) ✅
- [x] Backend FastAPI con modelos Elo + Dixon-Coles
- [x] Frontend Vue.js con 6 vistas
- [x] Simulación Monte Carlo del torneo
- [x] Tracking de resultados en vivo

### Fase 2 ✅
- [x] Entrenamiento XGBoost con ~7,000 partidos históricos
- [x] Ensemble de modelos (Elo 20% + Dixon-Coles 50% + XGBoost 30%)
- [x] Autenticación JWT para panel admin
- [x] Gráficos interactivos Chart.js
- [x] Modo oscuro/claro toggle
- [x] Notificaciones de resultados
- [x] Dashboard de accuracy (predicciones vs resultados reales)
- [x] Posiciones reales y bracket desde resultados registrados
- [x] Datos oficiales FIFA 2026 (48 equipos, 12 grupos, 12 resultados)
- [x] Dockerfile para Railway

### Fase 3 (Próximamente)
- [ ] Despliegue en Railway
- [ ] Scraping automático diario de resultados
- [ ] Historial de predicciones por usuario
- [ ] Exportación de datos (CSV/PDF)
- [ ] API pública documentada en Swagger
