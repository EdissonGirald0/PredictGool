const BASE_URL = '/api'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${BASE_URL}${path}`
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `HTTP ${res.status}`)
  }
  return res.json()
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    }),
}

export interface Team {
  id: string
  name: string
  group: string
  elo: number
  fifa_rank: number | null
  flag_emoji: string
}

export interface Group {
  id: string
  name: string
  teams: Team[]
}

export interface PredictResult {
  team_a: string
  team_b: string
  win: number
  draw: number
  loss: number
  expected_goals_a: number
  expected_goals_b: number
  most_likely_score: string
  top_scorelines: { goals_a: number; goals_b: number; probability: number }[]
}

export interface ChampionProb {
  team_name: string
  probability: number
  color_rank: number
}

export interface MonteCarloResult {
  total_simulations: number
  champion_probabilities: ChampionProb[]
  top_favorites: ChampionProb[]
}

export interface MatchResult {
  id: string
  team_a: string
  team_b: string
  score_a: number
  score_b: number
  stage: string
  group: string | null
  date: string
  played: boolean
}

export interface Fixture {
  id: number
  stage: string
  round: string
  group: string | null
  team_a: string | null
  team_b: string | null
  date: string
  venue: string
  score_a: number | null
  score_b: number | null
  played: boolean
}

export interface StandingRow {
  team_id: string
  team_name: string
  pts: number
  played: number
  w: number
  d: number
  l: number
  gf: number
  ga: number
  gd: number
  position: number
}

export interface StandingsData {
  standings: Record<string, StandingRow[]>
  classified: Record<string, string[]>
  best_thirds: string[]
  all_thirds_sorted: { team_name: string; pts: number; gd: number; gf: number }[]
  qualified_r32: string[]
}

export interface BracketStage {
  id: number
  date: string
  team_a: string
  team_b: string
  score_a: number | null
  score_b: number | null
  played: boolean
}

export interface CurrentBracket {
  stages: Record<string, BracketStage[]>
  standings: Record<string, StandingRow[]>
  classified: Record<string, string[]>
  best_thirds: string[]
  qualified_r32: string[]
  groups_complete: boolean
  total_knockout_matches: number
}
