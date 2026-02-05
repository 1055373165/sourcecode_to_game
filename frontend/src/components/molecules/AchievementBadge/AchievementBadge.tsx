import React from 'react'
import { cn } from '@utils/index'
import { Badge } from '@components/atoms/Badge'
import { type Achievement } from '@apptypes/index'
import { Lock } from 'lucide-react'

export interface AchievementBadgeProps {
    achievement: Achievement
    unlocked?: boolean
    progress?: number
    onClick?: () => void
    className?: string
}

export const AchievementBadge: React.FC<AchievementBadgeProps> = ({
    achievement,
    unlocked = false,
    progress = 0,
    onClick,
    className,
}) => {
    return (
        <div
            className={cn(
                'relative bg-white dark:bg-dark-surface rounded-lg p-4',
                'border-2 transition-all duration-200',
                unlocked
                    ? 'border-yellow-400 shadow-lg hover:shadow-xl cursor-pointer'
                    : 'border-gray-200 dark:border-gray-700 opacity-60 grayscale',
                onClick && 'cursor-pointer',
                className
            )}
            onClick={onClick}
            role={onClick ? 'button' : undefined}
            tabIndex={onClick ? 0 : undefined}
        >
            {/* Lock overlay for locked achievements */}
            {!unlocked && (
                <div className="absolute inset-0 flex items-center justify-center bg-gray-900/10 dark:bg-gray-900/40 rounded-lg">
                    <Lock className="w-6 h-6 text-gray-600 dark:text-gray-400" />
                </div>
            )}

            {/* Icon */}
            <div className="text-center mb-2">
                <span className={cn(
                    'text-4xl',
                    !unlocked && 'filter grayscale'
                )}>
                    {achievement.icon}
                </span>
            </div>

            {/* Name */}
            <h4 className="text-center font-semibold text-sm mb-1 text-gray-900 dark:text-gray-100">
                {achievement.name}
            </h4>

            {/* Description */}
            <p className="text-xs text-center text-gray-600 dark:text-gray-400 mb-2 line-clamp-2">
                {achievement.description}
            </p>

            {/* Category Badge */}
            <div className="flex justify-center mb-2">
                <Badge variant="achievement" category={achievement.category} className="text-xs">
                    {achievement.category}
                </Badge>
            </div>

            {/* XP Reward */}
            <div className="text-center text-xs font-medium text-primary-600 dark:text-primary-400">
                +{achievement.xp_reward} XP
            </div>

            {/* Progress Bar (if not unlocked) */}
            {!unlocked && progress > 0 && (
                <div className="mt-3">
                    <div className="h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-primary-500 rounded-full transition-all duration-300"
                            style={{ width: `${Math.min(progress, 100)}%` }}
                        />
                    </div>
                    <p className="text-xs text-center text-gray-500 dark:text-gray-400 mt-1">
                        {progress.toFixed(0)}% complete
                    </p>
                </div>
            )}

            {/* Unlocked Date */}
            {unlocked && achievement.unlocked_at && (
                <div className="mt-2 text-xs text-center text-gray-500 dark:text-gray-400">
                    Unlocked {new Date(achievement.unlocked_at).toLocaleDateString()}
                </div>
            )}
        </div>
    )
}
