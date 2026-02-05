import React from 'react'
import { cn, getDifficultyColor } from '@utils/index'
import { Difficulty, AchievementCategory } from '@apptypes/index'

export interface BadgeProps {
    children: React.ReactNode
    variant?: 'default' | 'difficulty' | 'achievement' | 'status'
    difficulty?: Difficulty
    category?: AchievementCategory
    className?: string
}

export const Badge: React.FC<BadgeProps> = ({
    children,
    variant = 'default',
    difficulty,
    category,
    className,
}) => {
    const baseStyles = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium'

    let styles = baseStyles

    if (variant === 'difficulty' && difficulty) {
        styles = cn(baseStyles, getDifficultyColor(difficulty))
    } else if (variant === 'achievement' && category) {
        const categoryColors: Record<AchievementCategory, string> = {
            [AchievementCategory.PROGRESSION]: 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300',
            [AchievementCategory.PERFORMANCE]: 'bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300',
            [AchievementCategory.SPECIAL]: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300',
            [AchievementCategory.SOCIAL]: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
        }
        styles = cn(baseStyles, categoryColors[category])
    } else if (variant === 'status') {
        styles = cn(baseStyles, 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300')
    } else {
        styles = cn(baseStyles, 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300')
    }

    return (
        <span className={cn(styles, className)}>
            {children}
        </span>
    )
}
