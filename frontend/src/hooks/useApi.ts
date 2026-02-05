/**
 * React Query hooks for API data fetching
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
    api,
    LoginResponse
} from '../api/client';

// Query keys
export const queryKeys = {
    user: ['user'] as const,
    userStats: ['userStats'] as const,
    userProgress: ['userProgress'] as const,
    userAchievements: ['userAchievements'] as const,
    projects: (params?: { language?: string; difficulty?: number }) =>
        ['projects', params] as const,
    project: (id: string) => ['project', id] as const,
    level: (id: string) => ['level', id] as const,
    projectProgress: (projectId: string) => ['projectProgress', projectId] as const,
};

// Auth hooks
export function useCurrentUser() {
    return useQuery({
        queryKey: queryKeys.user,
        queryFn: () => api.getCurrentUser(),
        enabled: api.isAuthenticated(),
        staleTime: 5 * 60 * 1000, // 5 minutes
        retry: false,
    });
}

export function useLogin() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ email, password }: { email: string; password: string }) =>
            api.login(email, password),
        onSuccess: (data: LoginResponse) => {
            queryClient.setQueryData(queryKeys.user, data.user);
            queryClient.invalidateQueries({ queryKey: queryKeys.userStats });
        },
    });
}

export function useRegister() {
    return useMutation({
        mutationFn: ({ username, email, password }: {
            username: string;
            email: string;
            password: string;
        }) => api.register(username, email, password),
    });
}

export function useLogout() {
    const queryClient = useQueryClient();

    return () => {
        api.logout();
        queryClient.clear();
    };
}

// User data hooks
export function useUserStats() {
    return useQuery({
        queryKey: queryKeys.userStats,
        queryFn: () => api.getUserStats(),
        enabled: api.isAuthenticated(),
        staleTime: 60 * 1000, // 1 minute
    });
}

export function useUserProgress() {
    return useQuery({
        queryKey: queryKeys.userProgress,
        queryFn: () => api.getUserProgress(),
        enabled: api.isAuthenticated(),
        staleTime: 60 * 1000,
    });
}

export function useUserAchievements() {
    return useQuery({
        queryKey: queryKeys.userAchievements,
        queryFn: () => api.getUserAchievements(),
        enabled: api.isAuthenticated(),
        staleTime: 5 * 60 * 1000,
    });
}

// Project hooks
export function useProjects(params?: { language?: string; difficulty?: number }) {
    return useQuery({
        queryKey: queryKeys.projects(params),
        queryFn: () => api.getProjects(params),
        enabled: api.isAuthenticated(),
        staleTime: 5 * 60 * 1000,
    });
}

export function useProject(id: string) {
    return useQuery({
        queryKey: queryKeys.project(id),
        queryFn: () => api.getProject(id),
        enabled: api.isAuthenticated() && !!id,
        staleTime: 5 * 60 * 1000,
    });
}

// Level hooks
export function useLevel(id: string) {
    return useQuery({
        queryKey: queryKeys.level(id),
        queryFn: () => api.getLevel(id),
        enabled: api.isAuthenticated() && !!id,
        staleTime: 60 * 1000,
    });
}

export function useSubmitLevel() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({
            levelId,
            answers,
            timeSpent
        }: {
            levelId: string;
            answers: Record<string, string>;
            timeSpent?: number;
        }) => api.submitLevel(levelId, answers, timeSpent),
        onSuccess: () => {
            // Invalidate related queries after submission
            queryClient.invalidateQueries({ queryKey: queryKeys.userStats });
            queryClient.invalidateQueries({ queryKey: queryKeys.userProgress });
            queryClient.invalidateQueries({ queryKey: queryKeys.userAchievements });
        },
    });
}

// Project progress hook
export function useProjectProgress(projectId: string) {
    return useQuery({
        queryKey: queryKeys.projectProgress(projectId),
        queryFn: () => api.getProjectProgress(projectId),
        enabled: api.isAuthenticated() && !!projectId,
        staleTime: 60 * 1000,
    });
}
