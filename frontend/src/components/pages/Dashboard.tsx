/**
 * Dashboard page - main landing page after login
 */
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useUserStats, useUserProgress, useUserAchievements, useProjects } from '../../hooks/useApi';

export function Dashboard() {
    const { user } = useAuth();
    const { data: stats, isLoading: statsLoading } = useUserStats();
    const { data: progress } = useUserProgress();
    const { data: achievements } = useUserAchievements();
    const { data: projects } = useProjects();

    if (statsLoading) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <div className="animate-spin w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full" />
            </div>
        );
    }

    const xpProgress = stats ? ((1000 - stats.xp_to_next_level) / 1000) * 100 : 0;
    const unlockedAchievements = achievements?.filter(a => a.unlocked) || [];

    return (
        <div className="p-6 space-y-6">
            {/* Welcome Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white">
                        Welcome back, <span className="text-purple-400">{user?.username}</span>! 👋
                    </h1>
                    <p className="text-slate-400 mt-1">Ready to continue your learning journey?</p>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {/* XP Card */}
                <div className="bg-gradient-to-br from-purple-900/50 to-pink-900/50 rounded-2xl p-5 border border-purple-500/20">
                    <div className="flex items-center justify-between mb-3">
                        <span className="text-3xl">⚡</span>
                        <span className="text-xs text-purple-300 bg-purple-500/20 px-2 py-1 rounded-full">
                            Level {stats?.current_level || 1}
                        </span>
                    </div>
                    <p className="text-2xl font-bold text-white">{stats?.total_xp || 0} XP</p>
                    <div className="mt-3">
                        <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
                            <div
                                className="h-full bg-gradient-to-r from-purple-500 to-pink-500"
                                style={{ width: `${xpProgress}%` }}
                            />
                        </div>
                        <p className="text-xs text-slate-500 mt-1">{stats?.xp_to_next_level || 0} XP to next level</p>
                    </div>
                </div>

                {/* Completed Card */}
                <div className="bg-slate-800/50 rounded-2xl p-5 border border-slate-700/50">
                    <span className="text-3xl">✅</span>
                    <p className="text-2xl font-bold text-white mt-3">{stats?.levels_completed || 0}</p>
                    <p className="text-sm text-slate-400">Levels Completed</p>
                </div>

                {/* Streak Card */}
                <div className="bg-slate-800/50 rounded-2xl p-5 border border-slate-700/50">
                    <span className="text-3xl">🔥</span>
                    <p className="text-2xl font-bold text-white mt-3">{stats?.current_streak || 0} days</p>
                    <p className="text-sm text-slate-400">Current Streak</p>
                </div>

                {/* Achievements Card */}
                <div className="bg-slate-800/50 rounded-2xl p-5 border border-slate-700/50">
                    <span className="text-3xl">🏆</span>
                    <p className="text-2xl font-bold text-white mt-3">{unlockedAchievements.length}</p>
                    <p className="text-sm text-slate-400">Achievements</p>
                </div>
            </div>

            {/* Continue Learning Section */}
            {progress && progress.length > 0 && (
                <div className="bg-slate-800/30 rounded-2xl p-6 border border-slate-700/50">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-xl font-semibold text-white">Continue Learning</h2>
                        <Link to="/projects" className="text-sm text-purple-400 hover:text-purple-300">
                            View all →
                        </Link>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {progress.slice(0, 3).map((p) => (
                            <Link
                                key={p.project_id}
                                to={`/projects/${p.project_id}`}
                                className="bg-slate-800/50 rounded-xl p-4 border border-slate-700/50 hover:border-purple-500/50 transition-all duration-300 group"
                            >
                                <h3 className="font-medium text-white group-hover:text-purple-300 transition">
                                    {p.project_name}
                                </h3>
                                <div className="mt-3">
                                    <div className="flex items-center justify-between text-sm mb-1">
                                        <span className="text-slate-400">
                                            {p.completed_levels} / {p.total_levels} levels
                                        </span>
                                        <span className="text-purple-400">{Math.round(p.completion_percentage)}%</span>
                                    </div>
                                    <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-gradient-to-r from-purple-500 to-pink-500"
                                            style={{ width: `${p.completion_percentage}%` }}
                                        />
                                    </div>
                                </div>
                            </Link>
                        ))}
                    </div>
                </div>
            )}

            {/* Quick Actions */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Link
                    to="/projects/create"
                    className="bg-gradient-to-br from-purple-900/50 to-pink-900/50 rounded-2xl p-6 border border-purple-500/30 hover:border-purple-500/50 transition-all duration-300 group"
                >
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-purple-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                            <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6 text-purple-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4" />
                                <path d="M9 18c-4.51 2-5-2-7-2" />
                            </svg>
                        </div>
                        <div className="flex-1">
                            <h3 className="text-lg font-semibold text-white group-hover:text-purple-300 transition">
                                Import GitHub Project
                            </h3>
                            <p className="text-sm text-slate-400 mt-0.5">
                                Add a new project from any public repository
                            </p>
                        </div>
                        <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 text-purple-400 group-hover:translate-x-1 transition-transform" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M5 12h14M12 5l7 7-7 7" />
                        </svg>
                    </div>
                </Link>

                <Link
                    to="/projects"
                    className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700/50 hover:border-slate-600 transition-all duration-300 group"
                >
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-slate-700/50 flex items-center justify-center group-hover:scale-110 transition-transform">
                            <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20" />
                            </svg>
                        </div>
                        <div className="flex-1">
                            <h3 className="text-lg font-semibold text-white group-hover:text-slate-200 transition">
                                Browse All Projects
                            </h3>
                            <p className="text-sm text-slate-400 mt-0.5">
                                Explore {projects?.total || 0} available projects
                            </p>
                        </div>
                        <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 text-slate-400 group-hover:translate-x-1 transition-transform" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M5 12h14M12 5l7 7-7 7" />
                        </svg>
                    </div>
                </Link>
            </div>

            {/* Available Projects */}
            {projects && projects.items.length > 0 && (

                <div className="bg-slate-800/30 rounded-2xl p-6 border border-slate-700/50">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-xl font-semibold text-white">Explore Projects</h2>
                        <Link to="/projects" className="text-sm text-purple-400 hover:text-purple-300">
                            Browse all →
                        </Link>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {projects.items.slice(0, 3).map((project) => (
                            <Link
                                key={project.id}
                                to={`/projects/${project.id}`}
                                className="bg-slate-800/50 rounded-xl p-4 border border-slate-700/50 hover:border-purple-500/50 transition-all duration-300 group"
                            >
                                <div className="flex items-center space-x-2 mb-2">
                                    <span className="px-2 py-0.5 text-xs bg-purple-500/20 text-purple-300 rounded">
                                        {project.language}
                                    </span>
                                    <span className="text-xs text-slate-500">
                                        {'⭐'.repeat(project.difficulty)}
                                    </span>
                                </div>
                                <h3 className="font-medium text-white group-hover:text-purple-300 transition">
                                    {project.name}
                                </h3>
                                <p className="text-sm text-slate-400 mt-1 line-clamp-2">
                                    {project.description || 'Explore this project to learn more'}
                                </p>
                                <p className="text-xs text-slate-500 mt-2">
                                    {project.total_levels} levels
                                </p>
                            </Link>
                        ))}
                    </div>
                </div>
            )}

            {/* Recent Achievements */}
            {unlockedAchievements.length > 0 && (
                <div className="bg-slate-800/30 rounded-2xl p-6 border border-slate-700/50">
                    <h2 className="text-xl font-semibold text-white mb-4">Recent Achievements</h2>
                    <div className="flex flex-wrap gap-3">
                        {unlockedAchievements.slice(0, 5).map((achievement) => (
                            <div
                                key={achievement.id}
                                className="flex items-center space-x-2 bg-slate-800/50 rounded-lg px-3 py-2 border border-slate-700/50"
                            >
                                <span className="text-2xl">{achievement.icon}</span>
                                <div>
                                    <p className="text-sm font-medium text-white">{achievement.name}</p>
                                    <p className="text-xs text-slate-400">{achievement.xp_reward} XP</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
