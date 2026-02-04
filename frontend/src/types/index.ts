/**
 * Core type definitions for the application
 * Matches backend service models
 */

export enum Language {
    PYTHON = 'PYTHON',
    GOLANG = 'GOLANG',
}

export enum NodeType {
    FUNCTION = 'FUNCTION',
    METHOD = 'METHOD',
    CLASS = 'CLASS',
}

export enum Difficulty {
    TUTORIAL = 'TUTORIAL',
    BASIC = 'BASIC',
    INTERMEDIATE = 'INTERMEDIATE',
    ADVANCED = 'ADVANCED',
    EXPERT = 'EXPERT',
}

export enum ChallengeType {
    MULTIPLE_CHOICE = 'MULTIPLE_CHOICE',
    CODE_TRACING = 'CODE_TRACING',
    FILL_BLANK = 'FILL_BLANK',
    CODE_COMPLETION = 'CODE_COMPLETION',
    DEBUGGING = 'DEBUGGING',
    ARCHITECTURE = 'ARCHITECTURE',
}

export enum LevelStatus {
    NOT_STARTED = 'NOT_STARTED',
    IN_PROGRESS = 'IN_PROGRESS',
    COMPLETED = 'COMPLETED',
}

export enum AchievementCategory {
    PROGRESSION = 'PROGRESSION',
    PERFORMANCE = 'PERFORMANCE',
    SPECIAL = 'SPECIAL',
    SOCIAL = 'SOCIAL',
}

export interface CodeNode {
    id: string
    name: string
    node_type: NodeType
    language: Language
    file_path: string
    line_start: number
    line_end: number
    parameters: Parameter[]
    return_type?: string
    decorators: string[]
    calls: string[]
    called_by: string[]
    docstring?: string
    complexity: number
    loc: number
}

export interface Parameter {
    name: string
    type_hint?: string
    default_value?: string
}

export interface CallEdge {
    from_node: string
    to_node: string
    call_count: number
}

export interface CallGraph {
    nodes: Record<string, CodeNode>
    edges: CallEdge[]
    entry_points: string[]
}

export interface Challenge {
    id: string
    type: ChallengeType
    question: Record<string, any>
    answer: Record<string, any>
    hints: string[]
    points: number
}

export interface Level {
    id: string
    name: string
    description: string
    difficulty: Difficulty
    entry_function: string
    call_chain: string[]
    code_snippet: string
    challenges: Challenge[]
    objectives: string[]
    xp_reward: number
    estimated_time: number
    prerequisites: string[]
}

export interface LevelProgress {
    user_id: string
    project_id: string
    level_id: string
    status: LevelStatus
    attempts: number
    best_score: number
    max_score: number
    completion_percentage: number
    is_perfect: boolean
    time_spent: number
    started_at?: string
    completed_at?: string
    hints_used: number
}

export interface ProjectProgress {
    user_id: string
    project_id: string
    project_name: string
    total_levels: number
    completed_levels: number
    completion_percentage: number
    is_completed: boolean
    current_level_id?: string
    total_xp_earned: number
    total_time_spent: number
    average_score: number
    started_at?: string
    completed_at?: string
    levels: LevelProgress[]
}

export interface UserStats {
    user_id: string
    total_xp: number
    current_level: number
    xp_to_next_level: number
    levels_completed: number
    projects_completed: number
    perfect_scores: number
    current_streak: number
    longest_streak: number
    last_activity_date?: string
    total_time_spent: number
}

export interface Achievement {
    id: string
    name: string
    description: string
    icon: string
    category: AchievementCategory
    xp_reward: number
    condition: Record<string, any>
    unlocked_at?: string
}

export interface LeaderboardEntry {
    rank: number
    user_id: string
    username: string
    score: number
    avatar?: string
    level?: number
}

export interface ChallengeResult {
    challenge_id: string
    is_correct: boolean
    points_earned: number
    max_points: number
    feedback: string
    hints: string[]
    execution_time?: number
}

export interface LevelResult {
    level_id: string
    level_completed: boolean
    score: number
    max_score: number
    percentage_score: number
    is_perfect_score: boolean
    is_first_attempt: boolean
    time_taken: number
    hints_used: number
    challenge_results: ChallengeResult[]
}

export interface LevelSubmission {
    level_id: string
    answers: Record<string, Record<string, any>>
    time_taken: number
}

export interface XPAward {
    amount: number
    reason: string
    breakdown: Record<string, number>
    timestamp: string
}

export interface LevelUp {
    old_level: number
    new_level: number
    xp_to_next: number
    rewards: string[]
}
