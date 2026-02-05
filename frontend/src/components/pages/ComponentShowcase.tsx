import React from 'react'
import { Button } from '@components/atoms/Button'
import { Badge } from '@components/atoms/Badge'
import { ProgressBar } from '@components/atoms/ProgressBar'
import { Difficulty } from '@apptypes/index'

// Temporary demo page to showcase atomic components
export const ComponentShowcase: React.FC = () => {
    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-dark-bg dark:to-dark-surface py-12 px-4">
            <div className="max-w-4xl mx-auto">
                <h1 className="text-4xl font-bold text-center mb-2 text-primary-600 dark:text-primary-400">
                    🎮 Study with Challenge
                </h1>
                <p className="text-center text-gray-600 dark:text-gray-400 mb-12">
                    Component Showcase
                </p>

                {/* Buttons Section */}
                <section className="bg-white dark:bg-dark-surface rounded-lg shadow-soft p-6 mb-6">
                    <h2 className="text-2xl font-semibold mb-4 text-gray-800 dark:text-gray-100">
                        Buttons
                    </h2>
                    <div className="flex flex-wrap gap-3">
                        <Button variant="primary" size="sm">Primary Small</Button>
                        <Button variant="primary" size="md">Primary Medium</Button>
                        <Button variant="primary" size="lg">Primary Large</Button>
                        <Button variant="secondary">Secondary</Button>
                        <Button variant="ghost">Ghost</Button>
                        <Button variant="danger">Danger</Button>
                        <Button variant="primary" disabled>Disabled</Button>
                        <Button variant="primary" isLoading>Loading...</Button>
                    </div>
                </section>

                {/* Badges Section */}
                <section className="bg-white dark:bg-dark-surface rounded-lg shadow-soft p-6 mb-6">
                    <h2 className="text-2xl font-semibold mb-4 text-gray-800 dark:text-gray-100">
                        Badges
                    </h2>
                    <div className="space-y-3">
                        <div>
                            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
                                Difficulty Levels
                            </h3>
                            <div className="flex flex-wrap gap-2">
                                <Badge variant="difficulty" difficulty={Difficulty.TUTORIAL}>Tutorial</Badge>
                                <Badge variant="difficulty" difficulty={Difficulty.BASIC}>Basic</Badge>
                                <Badge variant="difficulty" difficulty={Difficulty.INTERMEDIATE}>Intermediate</Badge>
                                <Badge variant="difficulty" difficulty={Difficulty.ADVANCED}>Advanced</Badge>
                                <Badge variant="difficulty" difficulty={Difficulty.EXPERT}>Expert</Badge>
                            </div>
                        </div>
                        <div>
                            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
                                Default Badges
                            </h3>
                            <div className="flex flex-wrap gap-2">
                                <Badge>Default</Badge>
                                <Badge variant="status">Status</Badge>
                                <Badge>🎯 With Icon</Badge>
                            </div>
                        </div>
                    </div>
                </section>

                {/* Progress Bars Section */}
                <section className="bg-white dark:bg-dark-surface rounded-lg shadow-soft p-6 mb-6">
                    <h2 className="text-2xl font-semibold mb-4 text-gray-800 dark:text-gray-100">
                        Progress Bars
                    </h2>
                    <div className="space-y-4">
                        <div>
                            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
                                Small (30%)
                            </h3>
                            <ProgressBar current={30} max={100} size="sm" />
                        </div>
                        <div>
                            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
                                Medium (60%)
                            </h3>
                            <ProgressBar current={60} max={100} size="md" />
                        </div>
                        <div>
                            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
                                Large (90%)
                            </h3>
                            <ProgressBar current={90} max={100} size="lg" />
                        </div>
                        <div>
                            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
                                XP Progress (1,250 / 2,000 XP)
                            </h3>
                            <ProgressBar current={1250} max={2000} size="md" animated />
                        </div>
                    </div>
                </section>

                {/* Combined Example */}
                <section className="bg-white dark:bg-dark-surface rounded-lg shadow-soft p-6">
                    <h2 className="text-2xl font-semibold mb-4 text-gray-800 dark:text-gray-100">
                        Combined Example: Level Card Preview
                    </h2>
                    <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                        <div className="flex justify-between items-start mb-3">
                            <div>
                                <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100">
                                    Understanding Flask Routes
                                </h3>
                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                    Learn how Flask routing works
                                </p>
                            </div>
                            <Badge variant="difficulty" difficulty={Difficulty.BASIC}>Basic</Badge>
                        </div>

                        <div className="mb-3">
                            <ProgressBar current={2} max={5} showLabel size="sm" />
                        </div>

                        <div className="flex gap-2 text-sm text-gray-600 dark:text-gray-400 mb-4">
                            <span>⏱️ ~10 min</span>
                            <span>•</span>
                            <span>💎 100 XP</span>
                            <span>•</span>
                            <span>📊 5 challenges</span>
                        </div>

                        <div className="flex gap-2">
                            <Button variant="primary" size="sm">Continue</Button>
                            <Button variant="ghost" size="sm">View Details</Button>
                        </div>
                    </div>
                </section>
            </div>
        </div>
    )
}
