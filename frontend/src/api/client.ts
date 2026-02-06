/**
 * TypeScript API client for Study with Challenge backend
 * All types and API methods for backend communication
 */

// Base configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Types
export interface User {
    id: string;
    username: string;
    email: string;
    is_active: boolean;
    total_xp: number;
    current_level: number;
    created_at: string;
}

export interface LoginResponse {
    access_token: string;
    token_type: string;
    user: User;
}

export interface Project {
    id: string;
    name: string;
    description: string | null;
    language: string;
    github_url: string | null;
    difficulty: number;
    total_levels: number;
    analysis_status: string;
    analyzed_at: string | null;
    created_at: string;
}

export interface Level {
    id: string;
    project_id: string;
    name: string;
    description: string | null;
    difficulty: number;
    entry_function: string | null;
    call_chain: string[] | null;
    code_snippet: string | null;
    xp_reward: number;
    estimated_time: number;
}

export interface Challenge {
    id: string;
    type: 'multiple_choice' | 'code_tracing' | 'fill_blank' | 'code_completion';
    question: Record<string, unknown>;
    hints: string[] | null;
    points: number;
}

export interface LevelDetail extends Level {
    challenges: Challenge[];
}

export interface UserStats {
    total_xp: number;
    current_level: number;
    xp_to_next_level: number;
    levels_completed: number;
    projects_completed: number;
    perfect_scores: number;
    current_streak: number;
    longest_streak: number;
    total_time_spent: number;
}

export interface ProjectProgress {
    project_id: string;
    project_name: string;
    total_levels: number;
    completed_levels: number;
    completion_percentage: number;
    average_score: number;
}

export interface Achievement {
    id: string;
    name: string;
    description: string;
    icon: string;
    category: string;
    xp_reward: number;
    unlocked: boolean;
    unlocked_at: string | null;
}

export interface SubmissionResult {
    success: boolean;
    score: number;
    max_score: number;
    xp_earned: number;
    results: ChallengeResult[];
    level_completed: boolean;
    new_achievements?: Achievement[];
}

export interface ChallengeResult {
    challenge_id: string;
    correct: boolean;
    points_earned: number;
    feedback?: string;
}

export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
}

export interface ApiError {
    error: {
        code: number;
        message: string;
        details?: unknown[];
        path?: string;
    };
}

// API Client class
class ApiClient {
    private baseUrl: string;
    private token: string | null = null;

    constructor(baseUrl: string = API_BASE_URL) {
        this.baseUrl = baseUrl;
        if (typeof window !== 'undefined') {
            this.token = localStorage.getItem('access_token');
        }
    }

    private async request<T>(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<T> {
        const headers: HeadersInit = {
            'Content-Type': 'application/json',
            ...options.headers,
        };

        if (this.token) {
            (headers as Record<string, string>)['Authorization'] = `Bearer ${this.token}`;
        }

        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            ...options,
            headers,
        });

        if (!response.ok) {
            const error: ApiError = await response.json();
            throw new Error(error.error?.message || 'API request failed');
        }

        return response.json();
    }

    setToken(token: string) {
        this.token = token;
        if (typeof window !== 'undefined') {
            localStorage.setItem('access_token', token);
        }
    }

    clearToken() {
        this.token = null;
        if (typeof window !== 'undefined') {
            localStorage.removeItem('access_token');
        }
    }

    isAuthenticated(): boolean {
        return !!this.token;
    }

    // Authentication endpoints
    async register(username: string, email: string, password: string): Promise<User> {
        return this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ username, email, password }),
        });
    }

    async login(email: string, password: string): Promise<LoginResponse> {
        const response = await this.request<LoginResponse>('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password }),
        });
        this.setToken(response.access_token);
        return response;
    }

    async getCurrentUser(): Promise<User> {
        return this.request('/auth/me');
    }

    logout() {
        this.clearToken();
    }

    // Project endpoints
    async getProjects(params?: {
        language?: string;
        difficulty?: number;
        page?: number;
        page_size?: number;
    }): Promise<PaginatedResponse<Project>> {
        const searchParams = new URLSearchParams();
        if (params) {
            Object.entries(params).forEach(([key, value]) => {
                if (value !== undefined) {
                    searchParams.set(key, String(value));
                }
            });
        }
        const queryString = searchParams.toString();
        return this.request(`/projects${queryString ? `?${queryString}` : ''}`);
    }

    async getProject(id: string): Promise<Project> {
        return this.request(`/projects/${id}`);
    }

    async getProjectLevels(projectId: string): Promise<{
        project_id: string;
        project_name: string;
        total_levels: number;
        levels: Array<{
            id: string;
            name: string;
            description: string | null;
            difficulty: number;
            entry_function: string | null;
            code_snippet: string | null;
            xp_reward: number;
            estimated_time: number;
            challenges_count: number;
            is_completed: boolean;
            score: number;
        }>;
    }> {
        return this.request(`/projects/${projectId}/levels`);
    }


    // Level endpoints
    async getLevel(id: string): Promise<LevelDetail> {
        return this.request(`/levels/${id}`);
    }

    async submitLevel(
        levelId: string,
        answers: Record<string, string>,
        timeSpent?: number
    ): Promise<SubmissionResult> {
        return this.request(`/levels/${levelId}/submit`, {
            method: 'POST',
            body: JSON.stringify({ answers, time_spent: timeSpent }),
        });
    }

    // User endpoints
    async getUserStats(): Promise<UserStats> {
        return this.request('/users/me/stats');
    }

    async getUserProgress(): Promise<ProjectProgress[]> {
        return this.request('/users/me/progress');
    }

    async getProjectProgress(projectId: string): Promise<ProjectProgress> {
        return this.request(`/users/me/progress/${projectId}`);
    }

    async getUserAchievements(): Promise<Achievement[]> {
        return this.request('/users/me/achievements');
    }

    // Health check
    async healthCheck(): Promise<{ status: string; database: string }> {
        return this.request('/health');
    }
}

// Export singleton instance
export const api = new ApiClient();

// Export class for custom instances
export { ApiClient };
