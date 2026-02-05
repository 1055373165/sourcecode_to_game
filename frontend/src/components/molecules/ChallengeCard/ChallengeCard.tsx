import React, { useState } from 'react'
import { cn } from '@utils/index'
import { Button } from '@components/atoms/Button'
import { Badge } from '@components/atoms/Badge'
import { type Challenge, ChallengeType } from '@apptypes/index'
import { CheckCircle2, Circle, HelpCircle } from 'lucide-react'

export interface ChallengeCardProps {
    challenge: Challenge
    userAnswer?: any
    isAnswered?: boolean
    isCorrect?: boolean
    showFeedback?: boolean
    onSubmit?: (answer: any) => void
    className?: string
}

export const ChallengeCard: React.FC<ChallengeCardProps> = ({
    challenge,
    userAnswer,
    isAnswered = false,
    isCorrect = false,
    showFeedback = false,
    onSubmit,
    className,
}) => {
    const [selectedAnswer, setSelectedAnswer] = useState<any>(userAnswer || null)
    const [showHint, setShowHint] = useState(false)

    const handleSubmit = () => {
        if (selectedAnswer !== null && onSubmit) {
            onSubmit(selectedAnswer)
        }
    }

    const renderChallengeInput = () => {
        switch (challenge.type) {
            case ChallengeType.MULTIPLE_CHOICE:
                const options = challenge.question.options || []
                return (
                    <div className="space-y-2">
                        {options.map((option: any, index: number) => {
                            const optionKey = String.fromCharCode(65 + index) // A, B, C, D
                            const isSelected = selectedAnswer === optionKey
                            const isAnsweredOption = isAnswered && userAnswer === optionKey
                            const isCorrectAnswer = isAnswered && challenge.answer.correct === optionKey

                            return (
                                <label
                                    key={optionKey}
                                    className={cn(
                                        'flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-all',
                                        'hover:bg-gray-50 dark:hover:bg-gray-800',
                                        isSelected && !isAnswered && 'border-primary-500 bg-primary-50 dark:bg-primary-900/20',
                                        isAnswered && isCorrectAnswer && 'border-success bg-green-50 dark:bg-green-900/20',
                                        isAnswered && isAnsweredOption && !isCorrect && 'border-error bg-red-50 dark:bg-red-900/20',
                                        !isAnswered && 'border-gray-200 dark:border-gray-700'
                                    )}
                                >
                                    <input
                                        type="radio"
                                        name={`challenge-${challenge.id}`}
                                        value={optionKey}
                                        checked={isSelected}
                                        onChange={() => setSelectedAnswer(optionKey)}
                                        disabled={isAnswered}
                                        className="w-4 h-4"
                                    />
                                    <span className="flex-1 text-gray-900 dark:text-gray-100">
                                        <span className="font-medium mr-2">{optionKey}.</span>
                                        {option}
                                    </span>
                                    {isAnswered && isCorrectAnswer && (
                                        <CheckCircle2 className="w-5 h-5 text-success" />
                                    )}
                                </label>
                            )
                        })}
                    </div>
                )

            case ChallengeType.FILL_BLANK:
                return (
                    <div className="space-y-2">
                        <input
                            type="text"
                            value={selectedAnswer || ''}
                            onChange={(e) => setSelectedAnswer(e.target.value)}
                            disabled={isAnswered}
                            placeholder="Type your answer..."
                            className={cn(
                                'w-full px-4 py-2 rounded-lg border',
                                'focus:outline-none focus:ring-2 focus:ring-primary-500',
                                'disabled:bg-gray-100 dark:disabled:bg-gray-800',
                                isAnswered && isCorrect && 'border-success',
                                isAnswered && !isCorrect && 'border-error',
                                'dark:bg-dark-surface dark:text-gray-100'
                            )}
                        />
                    </div>
                )

            default:
                return (
                    <div className="text-sm text-gray-500 italic">
                        Challenge type not yet implemented in preview
                    </div>
                )
        }
    }

    return (
        <div
            className={cn(
                'bg-white dark:bg-dark-surface rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-5',
                isAnswered && isCorrect && 'border-l-4 border-l-success',
                isAnswered && !isCorrect && 'border-l-4 border-l-error',
                className
            )}
        >
            {/* Header */}
            <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-2">
                    {isAnswered ? (
                        isCorrect ? (
                            <CheckCircle2 className="w-5 h-5 text-success flex-shrink-0" />
                        ) : (
                            <Circle className="w-5 h-5 text-error flex-shrink-0" />
                        )
                    ) : (
                        <Circle className="w-5 h-5 text-gray-400 flex-shrink-0" />
                    )}
                    <div>
                        <Badge variant="default" className="mb-1">
                            {challenge.type.replace('_', ' ')}
                        </Badge>
                    </div>
                </div>
                <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
                    {challenge.points} pts
                </span>
            </div>

            {/* Question */}
            <div className="mb-4">
                <p className="text-gray-900 dark:text-gray-100 font-medium mb-3">
                    {challenge.question.prompt}
                </p>
                {challenge.question.code && (
                    <pre className="bg-gray-50 dark:bg-gray-900 p-3 rounded-lg text-sm overflow-x-auto mb-3">
                        <code className="text-gray-800 dark:text-gray-200">
                            {challenge.question.code}
                        </code>
                    </pre>
                )}
            </div>

            {/* Input */}
            <div className="mb-4">
                {renderChallengeInput()}
            </div>

            {/* Feedback */}
            {showFeedback && isAnswered && (
                <div className={cn(
                    'p-3 rounded-lg mb-4 text-sm',
                    isCorrect ? 'bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-200' : 'bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-200'
                )}>
                    {isCorrect ? '✓ Correct!' : '✗ Incorrect. Try reviewing the hint below.'}
                </div>
            )}

            {/* Hints */}
            {challenge.hints && challenge.hints.length > 0 && (
                <div className="mb-4">
                    <button
                        onClick={() => setShowHint(!showHint)}
                        className="flex items-center gap-2 text-sm text-primary-600 dark:text-primary-400 hover:underline"
                    >
                        <HelpCircle className="w-4 h-4" />
                        {showHint ? 'Hide' : 'Show'} Hint
                    </button>
                    {showHint && (
                        <div className="mt-2 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg text-sm text-gray-700 dark:text-gray-300">
                            💡 {challenge.hints[0]}
                        </div>
                    )}
                </div>
            )}

            {/* Submit Button */}
            {!isAnswered && (
                <Button
                    variant="primary"
                    size="sm"
                    onClick={handleSubmit}
                    disabled={selectedAnswer === null}
                >
                    Submit Answer
                </Button>
            )}
        </div>
    )
}
