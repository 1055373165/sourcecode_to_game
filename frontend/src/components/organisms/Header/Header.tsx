/**
 * Header navigation component
 */
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../../contexts/AuthContext';
import { useUserStats } from '../../../hooks/useApi';

export function Header() {
    const { user, logout, isAuthenticated } = useAuth();
    const { data: stats } = useUserStats();
    const location = useLocation();

    const navLinks = [
        { path: '/dashboard', label: 'Dashboard' },
        { path: '/projects', label: 'Projects' },
        { path: '/leaderboard', label: 'Leaderboard' },
    ];

    const isActive = (path: string) => location.pathname === path;

    return (
        <header className="bg-slate-900/80 backdrop-blur-xl border-b border-slate-700/50 sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    {/* Logo */}
                    <Link to="/dashboard" className="flex items-center space-x-2">
                        <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                            <span className="text-white font-bold text-lg">S</span>
                        </div>
                        <span className="text-xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent hidden sm:block">
                            Study Challenge
                        </span>
                    </Link>

                    {/* Navigation */}
                    {isAuthenticated && (
                        <nav className="hidden md:flex items-center space-x-1">
                            {navLinks.map((link) => (
                                <Link
                                    key={link.path}
                                    to={link.path}
                                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${isActive(link.path)
                                        ? 'bg-purple-500/20 text-purple-300'
                                        : 'text-slate-400 hover:text-white hover:bg-slate-800'
                                        }`}
                                >
                                    {link.label}
                                </Link>
                            ))}
                        </nav>
                    )}

                    {/* User section */}
                    {isAuthenticated && user ? (
                        <div className="flex items-center space-x-4">
                            {/* XP Display */}
                            {stats && (
                                <div className="hidden sm:flex items-center space-x-2 px-3 py-1.5 bg-slate-800/50 rounded-lg border border-slate-700/50">
                                    <span className="text-yellow-400 text-sm">⚡</span>
                                    <span className="text-sm font-medium text-white">{stats.total_xp} XP</span>
                                    <span className="text-xs text-slate-500">Lv.{stats.current_level}</span>
                                </div>
                            )}

                            {/* User menu */}
                            <div className="flex items-center space-x-3">
                                <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-full flex items-center justify-center">
                                    <span className="text-white text-sm font-medium">
                                        {user.username[0].toUpperCase()}
                                    </span>
                                </div>
                                <div className="hidden sm:block">
                                    <p className="text-sm font-medium text-white">{user.username}</p>
                                </div>
                                <button
                                    onClick={logout}
                                    className="px-3 py-1.5 text-sm text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition"
                                >
                                    Logout
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div className="flex items-center space-x-3">
                            <Link
                                to="/login"
                                className="px-4 py-2 text-sm font-medium text-slate-300 hover:text-white transition"
                            >
                                Sign In
                            </Link>
                            <Link
                                to="/register"
                                className="px-4 py-2 text-sm font-medium bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-500 hover:to-pink-500 transition"
                            >
                                Get Started
                            </Link>
                        </div>
                    )}
                </div>
            </div>
        </header>
    );
}
