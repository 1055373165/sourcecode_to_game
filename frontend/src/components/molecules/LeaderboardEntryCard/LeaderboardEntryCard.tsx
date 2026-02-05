import React from 'react'
import { cn } from '@utils/index'
import { type LeaderboardEntry } from '@apptypes/index'
import { Trophy, TrendingUp } from 'lucide-react'

export interface LeaderboardEntryCardProps {
    entry: LeaderboardEntry
    isCurrentUser?: boolean
    showTrend?: boolean
    className?: string
}

export const LeaderboardEntryCard: React.FC<LeaderboardEntryCardProps> = ({
    entry,
    isCurrentUser = false,
    showTrend = false,
    className,
}) => {
    const getRankColor = (rank: number) => {
        if (rank === 1) return 'text-yellow-500'
        if (rank === 2) return 'text-gray-400'
        if (rank === 3) return 'text-orange-600'
        return 'text-gray-600 dark:text-gray-400'
    }

    const getRankIcon = (rank: number) => {
        if (rank <= 3) {
            return <Trophy className={cn('w-5 h-5', getRankColor(rank))} />
        }
        return null
    }

    return (
        <div
            className={cn(
                'flex items-center gap-4 p-4 rounded-lg transition-all',
                isCurrentUser
                    ? 'bg-primary-50 dark:bg-primary-900/20 border-2 border-primary-500'
                    : 'bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 hover:shadow-sm',
                className
            )}
        >
            {/* Rank */}
            <div className="flex items-center justify-center w-12">
                {getRankIcon(entry.rank) || (
                    <span className={cn('text-lg font-bold', getRankColor(entry.rank))}>
                        #{entry.rank}
                    </span>
                )}
            </div>

            {/* Avatar & Info */}
            <div className="flex items-center gap-3 flex-1 min-w-0">
                {entry.avatar ? (
                    <img
                        src={entry.avatar}
                        alt={entry.username}
                        className="w-10 h-10 rounded-full border-2 border-gray-200 dark:border-gray-700"
                    />
                ) : (
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center text-white font-semibold">
                        {entry.username.charAt(0).toUpperCase()}
                    </div>
                )}

                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                        <p className="font-semibold text-gray-900 dark:text-gray-100 truncate">
                            {entry.username}
                        </p>
                        {isCurrentUser && (
                            <span className="text-xs font-medium text-primary-600 dark:text-primary-400 px-2 py-0.5 bg-primary-100 dark:bg-primary-900/40 rounded-full">
                                You
                            </span>
                        )}
                    </div>
                    {entry.level !== undefined && (
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                            Level {entry.level}
                        </p>
                    )}
                </div>
            </div>

            {/* Score */}
            <div className="text-right">
                <p className="text-lg font-bold text-gray-900 dark:text-gray-100">
                    {entry.score.toLocaleString()}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                    XP
                </p>
            </div>

            {/* Trend (optional) */}
            {showTrend && (
                <div className="flex items-center gap-1 text-success">
                    <TrendingUp className="w-4 h-4" />
                    <span className="text-sm font-medium">+5</span>
                </div>
            )}
        </div>
    )
}
