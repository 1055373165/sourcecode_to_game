/**
 * Leaderboard page
 */
import { useState } from 'react';

// Mock data for demonstration (will be replaced with API call)
const mockLeaderboard = [
    { rank: 1, username: 'codemaster', xp: 15000, level: 15, streak: 42, avatar: '👨‍💻' },
    { rank: 2, username: 'pythonista', xp: 12500, level: 13, streak: 35, avatar: '🐍' },
    { rank: 3, username: 'devguru', xp: 11000, level: 11, streak: 28, avatar: '🚀' },
    { rank: 4, username: 'codewizard', xp: 9500, level: 10, streak: 21, avatar: '🧙' },
    { rank: 5, username: 'hackerman', xp: 8200, level: 9, streak: 18, avatar: '💻' },
    { rank: 6, username: 'techie', xp: 7500, level: 8, streak: 15, avatar: '⚡' },
    { rank: 7, username: 'coder101', xp: 6800, level: 7, streak: 12, avatar: '📚' },
    { rank: 8, username: 'debugger', xp: 5900, level: 6, streak: 10, avatar: '🔍' },
    { rank: 9, username: 'newbie', xp: 4500, level: 5, streak: 7, avatar: '🌱' },
    { rank: 10, username: 'learner', xp: 3200, level: 4, streak: 5, avatar: '📖' },
];

type TabType = 'xp' | 'streak' | 'levels';

export function Leaderboard() {
    const [activeTab, setActiveTab] = useState<TabType>('xp');

    const tabs: { id: TabType; label: string; icon: string }[] = [
        { id: 'xp', label: 'XP Leaders', icon: '⚡' },
        { id: 'streak', label: 'Top Streaks', icon: '🔥' },
        { id: 'levels', label: 'Most Levels', icon: '📈' },
    ];

    const getRankStyle = (rank: number) => {
        switch (rank) {
            case 1:
                return 'bg-gradient-to-r from-yellow-500/20 to-amber-500/20 border-yellow-500/30';
            case 2:
                return 'bg-gradient-to-r from-slate-400/20 to-gray-400/20 border-slate-400/30';
            case 3:
                return 'bg-gradient-to-r from-orange-500/20 to-amber-600/20 border-orange-500/30';
            default:
                return 'bg-slate-800/50 border-slate-700/50';
        }
    };

    const getRankIcon = (rank: number) => {
        switch (rank) {
            case 1:
                return '🥇';
            case 2:
                return '🥈';
            case 3:
                return '🥉';
            default:
                return `#${rank}`;
        }
    };

    return (
        <div className="p-6 space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-white">Leaderboard</h1>
                <p className="text-slate-400 mt-1">See how you rank against other learners</p>
            </div>

            {/* Tabs */}
            <div className="flex space-x-2">
                {tabs.map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition ${activeTab === tab.id
                            ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
                            : 'text-slate-400 hover:text-white hover:bg-slate-800'
                            }`}
                    >
                        <span>{tab.icon}</span>
                        <span className="font-medium">{tab.label}</span>
                    </button>
                ))}
            </div>

            {/* Top 3 Podium */}
            <div className="grid grid-cols-3 gap-4 mb-6">
                {/* 2nd Place */}
                <div className={`rounded-xl p-5 border ${getRankStyle(2)} text-center order-1`}>
                    <span className="text-4xl">{mockLeaderboard[1].avatar}</span>
                    <span className="text-3xl ml-1">🥈</span>
                    <p className="font-semibold text-white mt-2">{mockLeaderboard[1].username}</p>
                    <p className="text-lg text-purple-400 font-bold">{mockLeaderboard[1].xp.toLocaleString()} XP</p>
                    <p className="text-xs text-slate-400">Level {mockLeaderboard[1].level}</p>
                </div>

                {/* 1st Place */}
                <div className={`rounded-xl p-6 border ${getRankStyle(1)} text-center order-0 transform scale-110`}>
                    <span className="text-5xl">{mockLeaderboard[0].avatar}</span>
                    <span className="text-4xl ml-1">🥇</span>
                    <p className="font-bold text-white mt-2 text-lg">{mockLeaderboard[0].username}</p>
                    <p className="text-xl text-yellow-400 font-bold">{mockLeaderboard[0].xp.toLocaleString()} XP</p>
                    <p className="text-sm text-slate-400">Level {mockLeaderboard[0].level}</p>
                </div>

                {/* 3rd Place */}
                <div className={`rounded-xl p-5 border ${getRankStyle(3)} text-center order-2`}>
                    <span className="text-4xl">{mockLeaderboard[2].avatar}</span>
                    <span className="text-3xl ml-1">🥉</span>
                    <p className="font-semibold text-white mt-2">{mockLeaderboard[2].username}</p>
                    <p className="text-lg text-orange-400 font-bold">{mockLeaderboard[2].xp.toLocaleString()} XP</p>
                    <p className="text-xs text-slate-400">Level {mockLeaderboard[2].level}</p>
                </div>
            </div>

            {/* Rest of Leaderboard */}
            <div className="bg-slate-800/30 rounded-xl border border-slate-700/50 overflow-hidden">
                <table className="w-full">
                    <thead>
                        <tr className="border-b border-slate-700/50">
                            <th className="px-6 py-4 text-left text-sm font-medium text-slate-400">Rank</th>
                            <th className="px-6 py-4 text-left text-sm font-medium text-slate-400">User</th>
                            <th className="px-6 py-4 text-right text-sm font-medium text-slate-400">XP</th>
                            <th className="px-6 py-4 text-right text-sm font-medium text-slate-400">Level</th>
                            <th className="px-6 py-4 text-right text-sm font-medium text-slate-400">Streak</th>
                        </tr>
                    </thead>
                    <tbody>
                        {mockLeaderboard.slice(3).map((user) => (
                            <tr
                                key={user.rank}
                                className={`border-b border-slate-700/30 hover:bg-slate-800/50 transition`}
                            >
                                <td className="px-6 py-4">
                                    <span className="text-slate-400 font-medium">{getRankIcon(user.rank)}</span>
                                </td>
                                <td className="px-6 py-4">
                                    <div className="flex items-center space-x-3">
                                        <span className="text-2xl">{user.avatar}</span>
                                        <span className="font-medium text-white">{user.username}</span>
                                    </div>
                                </td>
                                <td className="px-6 py-4 text-right">
                                    <span className="text-purple-400 font-medium">{user.xp.toLocaleString()}</span>
                                </td>
                                <td className="px-6 py-4 text-right">
                                    <span className="text-slate-300">{user.level}</span>
                                </td>
                                <td className="px-6 py-4 text-right">
                                    <span className="text-orange-400">{user.streak} 🔥</span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Your Position */}
            <div className="bg-gradient-to-r from-purple-900/30 to-pink-900/30 rounded-xl p-5 border border-purple-500/20">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                        <span className="text-2xl">👤</span>
                        <div>
                            <p className="text-sm text-slate-400">Your Position</p>
                            <p className="text-lg font-bold text-white">#42</p>
                        </div>
                    </div>
                    <div className="text-right">
                        <p className="text-sm text-slate-400">Current XP</p>
                        <p className="text-lg font-bold text-purple-400">1,500 XP</p>
                    </div>
                    <div className="text-right">
                        <p className="text-sm text-slate-400">To next rank</p>
                        <p className="text-lg font-bold text-green-400">+500 XP</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
