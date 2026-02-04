import React from 'react'
import { cn, getProgressColor } from '@utils/index'

export interface ProgressBarProps {
    current: number
    max: number
    showLabel?: boolean
    showPercentage?: boolean
    size?: 'sm' | 'md' | 'lg'
    animated?: boolean
    className?: string
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
    current,
    max,
    showLabel = true,
    showPercentage = true,
    size = 'md',
    animated = true,
    className,
}) => {
    const percentage = max > 0 ? Math.min(100, (current / max) * 100) : 0

    const sizeStyles = {
        sm: 'h-1.5',
        md: 'h-2.5',
        lg: 'h-3.5',
    }

    return (
        <div className={cn('w-full', className)}>
            {showLabel && (
                <div className="flex justify-between items-center mb-1 text-sm">
                    <span className="font-medium text-gray-700 dark:text-gray-300">
                        {current} / {max}
                    </span>
                    {showPercentage && (
                        <span className="text-gray-500 dark:text-gray-400">
                            {percentage.toFixed(0)}%
                        </span>
                    )}
                </div>
            )}

            <div className={cn(
                'w-full bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden',
                sizeStyles[size]
            )}>
                <div
                    className={cn(
                        'h-full rounded-full transition-all duration-500 ease-out',
                        getProgressColor(percentage),
                        animated && 'animate-pulse-slow'
                    )}
                    style={{ width: `${percentage}%` }}
                    role="progressbar"
                    aria-valuenow={current}
                    aria-valuemin={0}
                    aria-valuemax={max}
                />
            </div>
        </div>
    )
}
