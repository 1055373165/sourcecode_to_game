/**
 * Sidebar navigation component
 */
import { Link, useLocation } from 'react-router-dom';
import { useUserStats, useUserProgress } from '../../../hooks/useApi';

interface SidebarProps {
    isOpen?: boolean;
    onClose?: () => void;
}

export function Sidebar({ isOpen = true, onClose }: SidebarProps) {
    const location = useLocation();
    const { data: stats } = useUserStats();
    const { data: progress } = useUserProgress();

    const navItems = [
        { path: '/dashboard', label: 'Dashboard', icon: '🏠' },
        { path: '/projects', label: 'Projects', icon: '📚' },
        { path: '/achievements', label: 'Achievements', icon: '🏆' },
        { path: '/leaderboard', label: 'Leaderboard', icon: '🥇' },
    ];

    const isActive = (path: string) => location.pathname.startsWith(path);

    // Calculate XP progress to next level
    const xpProgress = stats ? ((1000 - stats.xp_to_next_level) / 1000) * 100 : 0;

    return (
        <aside
            className={`fixed lg:static inset-y-0 left-0 z-40 w-64 bg-slate-900 border-r border-slate-700/50 transform transition-transform duration-300 ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
                }`}
        >
            <div className="flex flex-col h-full pt-20 lg:pt-4 pb-4">
                {/* User Stats Card */}
                {stats && (
                    <div className="mx-4 mb-6 p-4 bg-gradient-to-br from-purple-900/50 to-pink-900/50 rounded-xl border border-purple-500/20">
                        <div className="flex items-center justify-between mb-3">
                            <span className="text-sm text-slate-400">Level {stats.current_level}</span>
                            <span className="text-sm font-medium text-purple-300">{stats.total_xp} XP</span>
                        </div>
                        {/* XP Progress Bar */}
                        <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                            <div
                                className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-500"
                                style={{ width: `${xpProgress}%` }}
                            />
                        </div>
                        <p className="text-xs text-slate-500 mt-2">
                            {stats.xp_to_next_level} XP to level {stats.current_level + 1}
                        </p>
                    </div>
                )}

                {/* Navigation */}
                <nav className="flex-1 px-3 space-y-1">
                    {navItems.map((item) => (
                        <Link
                            key={item.path}
                            to={item.path}
                            onClick={onClose}
                            className={`flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-200 ${isActive(item.path)
                                ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
                                : 'text-slate-400 hover:text-white hover:bg-slate-800'
                                }`}
                        >
                            <span className="text-lg">{item.icon}</span>
                            <span className="font-medium">{item.label}</span>
                        </Link>
                    ))}
                </nav>

                {/* Progress Summary */}
                {progress && progress.length > 0 && (
                    <div className="mx-4 mt-4 p-4 bg-slate-800/50 rounded-xl">
                        <h4 className="text-sm font-medium text-white mb-3">Progress</h4>
                        <div className="space-y-2">
                            {progress.slice(0, 3).map((p) => (
                                <div key={p.project_id} className="flex items-center justify-between">
                                    <span className="text-xs text-slate-400 truncate max-w-[120px]">
                                        {p.project_name}
                                    </span>
                                    <span className="text-xs text-purple-400">
                                        {Math.round(p.completion_percentage)}%
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Quick Stats */}
                {stats && (
                    <div className="mx-4 mt-4 grid grid-cols-2 gap-2">
                        <div className="p-3 bg-slate-800/50 rounded-lg text-center">
                            <p className="text-lg font-bold text-white">{stats.levels_completed}</p>
                            <p className="text-xs text-slate-500">Completed</p>
                        </div>
                        <div className="p-3 bg-slate-800/50 rounded-lg text-center">
                            <p className="text-lg font-bold text-white">{stats.current_streak}</p>
                            <p className="text-xs text-slate-500">Streak 🔥</p>
                        </div>
                    </div>
                )}
            </div>
        </aside>
    );
}
