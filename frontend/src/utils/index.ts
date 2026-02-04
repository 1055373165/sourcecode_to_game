import { type ClassValue, clsx } from 'clsx'

export function cn(...inputs: ClassValue[]) {
    return clsx(inputs)
}

export function formatTime(seconds: number): string {
    if (seconds < 60) {
        return `${seconds}s`
    }
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    if (minutes < 60) {
        return `${minutes}m ${remainingSeconds}s`
    }
    const hours = Math.floor(minutes / 60)
    const remainingMinutes = minutes % 60
    return `${hours}h ${remainingMinutes}m`
}

export function formatNumber(num: number): string {
    if (num >= 1000000) {
        return `${(num / 1000000).toFixed(1)}M`
    }
    if (num >= 1000) {
        return `${(num / 1000).toFixed(1)}K`
    }
    return num.toString()
}

export function getDifficultyColor(difficulty: string): string {
    const colors: Record<string, string> = {
        TUTORIAL: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
        BASIC: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
        INTERMEDIATE: 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300',
        ADVANCED: 'bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300',
        EXPERT: 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300',
    }
    return colors[difficulty] || colors.BASIC
}

export function getProgressColor(percentage: number): string {
    if (percentage >= 90) return 'bg-green-500'
    if (percentage >= 70) return 'bg-blue-500'
    if (percentage >= 50) return 'bg-yellow-500'
    return 'bg-orange-500'
}
