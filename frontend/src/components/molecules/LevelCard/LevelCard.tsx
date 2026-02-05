import React from 'react'
import { cn } from '@utils/index'
import { Badge } from '@components/atoms/Badge'
import { ProgressBar } from '@components/atoms/ProgressBar'
import { Button } from '@components/atoms/Button'
import { type Level, type LevelProgress } from '@apptypes/index'
import { Clock, Award, Target } from 'lucide-react'

export interface LevelCardProps {
    level: Level
    progress?: LevelProgress
    onClick?: () => void
    className?: string
}

export const LevelCard: React.FC<LevelCardProps> = ({
    level,
    progress,
    onClick,
    className,
}) => {
    const isCompleted = progress?.status === 'COMPLETED'
    const isInProgress = progress?.status === 'IN_PROGRESS'
    const isLocked = !progress || progress.status === 'NOT_STARTED'

    const isPerfect = progress?.is_perfect || false


    return (
        <div
            className={cn(
                'bg-white dark:bg-dark-surface rounded-lg shadow-sm hover:shadow-md transition-all duration-200',
                'border border-gray-200 dark:border-gray-700',
                'p-5 cursor-pointer',
                isCompleted && 'border-l-4 border-l-success',
                isInProgress && 'border-l-4 border-l-blue-500',
                className
            )}
            onClick={onClick}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault()
                    onClick?.()
                }
            }}
        >
            {/* Header */}
            <div className="flex justify-between items-start mb-3">
                <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-1">
                        {level.name}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                        {level.description}
                    </p>
                </div>
                <Badge variant="difficulty" difficulty={level.difficulty}>
                    {level.difficulty}
                </Badge>
            </div>

            {/* Progress Bar */}
            {progress && progress.status !== 'NOT_STARTED' && (
                <div className="mb-3">
                    <ProgressBar
                        current={progress.best_score}
                        max={progress.max_score}
                        showLabel={false}
                        showPercentage={true}
                        size="sm"
                    />
                </div>
            )}

            {/* Metadata */}
            <div className="flex flex-wrap gap-3 text-sm text-gray-600 dark:text-gray-400 mb-4">
                <div className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    <span>~{level.estimated_time} min</span>
                </div>
                <div className="flex items-center gap-1">
                    <Award className="w-4 h-4" />
                    <span>{level.xp_reward} XP</span>
                </div>
                <div className="flex items-center gap-1">
                    <Target className="w-4 h-4" />
                    <span>{level.challenges.length} challenges</span>
                </div>
            </div>

            {/* Status & Actions */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    {isCompleted && (
                        <span className="text-sm font-medium text-success flex items-center gap-1">
                            ✓ Completed
                            {isPerfect && <span className="text-xs">⭐ Perfect</span>}
                        </span>
                    )}
                    {isInProgress && (
                        <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
                            In Progress
                        </span>
                    )}
                    {isLocked && (
                        <span className="text-sm text-gray-500 dark:text-gray-500">
                            Not Started
                        </span>
                    )}
                    {progress && progress.attempts > 0 && (
                        <span className="text-xs text-gray-500">
                            ({progress.attempts} {progress.attempts === 1 ? 'attempt' : 'attempts'})
                        </span>
                    )}
                </div>

                <Button
                    variant={isCompleted ? 'secondary' : 'primary'}
                    size="sm"
                >
                    {isCompleted ? 'Review' : isInProgress ? 'Continue' : 'Start'}
                </Button>
            </div>
        </div>
    )
}
