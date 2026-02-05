import React, { useState } from 'react'
import { LevelCard } from '@components/molecules/LevelCard'
import { ChallengeCard } from '@components/molecules/ChallengeCard'
import { AchievementBadge } from '@components/molecules/AchievementBadge'
import { LeaderboardEntryCard } from '@components/molecules/LeaderboardEntryCard'
import { CodeViewer } from '@components/organisms/CodeViewer'
import { CallGraphViewer } from '@components/organisms/CallGraphViewer'
import {
    Difficulty,
    ChallengeType,
    Language,
    NodeType,
    AchievementCategory,
    type Level,
    type LevelProgress,
    type Achievement,
    type LeaderboardEntry,
    type CodeNode,
    type CallEdge,
} from '@apptypes/index'


// Sample data
const sampleLevel: Level = {
    id: 'level-1',
    name: 'Understanding Flask Routes',
    description: 'Learn how Flask routing works by exploring a simple web application',
    difficulty: Difficulty.BASIC,
    entry_function: 'index',
    call_chain: ['index', 'route', 'Response'],
    code_snippet: `@app.route('/index')
def index():
    return "Hello World"`,
    challenges: [
        {
            id: 'ch-1',
            type: ChallengeType.MULTIPLE_CHOICE,
            question: {
                prompt: 'What decorator is used for routing in Flask?',
                options: ['@app.route', '@route', '@flask.route', '@web.route'],
            },
            answer: { correct: 'A' },
            hints: ['Look at the code snippet above'],
            points: 10,
        }
    ],
    objectives: ['Understand Flask decorators'],
    xp_reward: 100,
    estimated_time: 10,
    prerequisites: [],
}

const sampleProgress: LevelProgress = {
    user_id: 'user-1',
    project_id: 'proj-1',
    level_id: 'level-1',
    status: 'IN_PROGRESS' as any,
    attempts: 2,
    best_score: 40,
    max_score: 50,
    completion_percentage: 80,
    is_perfect: false,
    time_spent: 300,
    hints_used: 1,
}

const sampleAchievement: Achievement = {
    id: 'first-steps',
    name: 'First Steps',
    description: 'Complete your first level',
    icon: '🎓',
    category: AchievementCategory.PROGRESSION,
    xp_reward: 50,
    condition: { type: 'levels_completed', count: 1 },
    unlocked_at: new Date().toISOString(),
}

const sampleLeaderboardEntries: LeaderboardEntry[] = [
    { rank: 1, user_id: 'u1', username: 'Alice', score: 2500, level: 5 },
    { rank: 2, user_id: 'u2', username: 'Bob', score: 1800, level: 4 },
    { rank: 3, user_id: 'u3', username: 'Charlie', score: 1200, level: 3 },
]

const sampleCode = `from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/about')
def about():
    return "About Page"

if __name__ == '__main__':
    app.run(debug=True)
`

const sampleNodes: CodeNode[] = [
    {
        id: 'index',
        name: 'index',
        node_type: NodeType.FUNCTION,
        language: Language.PYTHON,
        file_path: 'app.py',
        line_start: 5,
        line_end: 7,
        parameters: [],
        decorators: ['@app.route("/")'],
        calls: [],
        called_by: [],
        complexity: 1,
        loc: 2,
    },
    {
        id: 'about',
        name: 'about',
        node_type: NodeType.FUNCTION,
        language: Language.PYTHON,
        file_path: 'app.py',
        line_start: 9,
        line_end: 11,
        parameters: [],
        decorators: ['@app.route("/about")'],
        calls: [],
        called_by: [],
        complexity: 1,
        loc: 2,
    },
]

const sampleEdges: CallEdge[] = []

export const ExtendedShowcase: React.FC = () => {
    const [theme, setTheme] = useState<'vs-dark' | 'light'>('vs-dark')

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-dark-bg dark:to-dark-surface py-12 px-4">
            <div className="max-w-7xl mx-auto">
                <h1 className="text-4xl font-bold text-center mb-2 text-primary-600 dark:text-primary-400">
                    🎮 Study with Challenge
                </h1>
                <p className="text-center text-gray-600 dark:text-gray-400 mb-12">
                    Extended Component Showcase
                </p>

                {/* Molecule Components */}
                <section className="mb-12">
                    <h2 className="text-3xl font-semibold mb-6 text-gray-800 dark:text-gray-100">
                        Molecule Components
                    </h2>

                    {/* Level Cards */}
                    <div className="mb-8">
                        <h3 className="text-xl font-semibold mb-4 text-gray-700 dark:text-gray-200">
                            Level Cards
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            <LevelCard level={sampleLevel} progress={sampleProgress} />
                            <LevelCard level={{ ...sampleLevel, id: 'level-2', name: 'Completed Level', difficulty: Difficulty.INTERMEDIATE }}
                                progress={{ ...sampleProgress, status: 'COMPLETED' as any, completion_percentage: 100, is_perfect: true, best_score: 50 }} />
                            <LevelCard level={{ ...sampleLevel, id: 'level-3', name: 'Not Started', difficulty: Difficulty.ADVANCED }} />
                        </div>
                    </div>

                    {/* Challenge Card */}
                    <div className="mb-8">
                        <h3 className="text-xl font-semibold mb-4 text-gray-700 dark:text-gray-200">
                            Challenge Card
                        </h3>
                        <div className="max-w-2xl">
                            <ChallengeCard challenge={sampleLevel.challenges[0]} />
                        </div>
                    </div>

                    {/* Achievement Badges */}
                    <div className="mb-8">
                        <h3 className="text-xl font-semibold mb-4 text-gray-700 dark:text-gray-200">
                            Achievement Badges
                        </h3>
                        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                            <AchievementBadge achievement={sampleAchievement} unlocked />
                            <AchievementBadge achievement={{ ...sampleAchievement, id: 'locked-1', name: 'Locked' }} progress={60} />
                            <AchievementBadge achievement={{ ...sampleAchievement, id: 'locked-2', name: 'Just Started' }} progress={10} />
                        </div>
                    </div>

                    {/* Leaderboard */}
                    <div className="mb-8">
                        <h3 className="text-xl font-semibold mb-4 text-gray-700 dark:text-gray-200">
                            Leaderboard Entries
                        </h3>
                        <div className="max-w-2xl space-y-2">
                            {sampleLeaderboardEntries.map(entry => (
                                <LeaderboardEntryCard
                                    key={entry.user_id}
                                    entry={entry}
                                    isCurrentUser={entry.rank === 2}
                                />
                            ))}
                        </div>
                    </div>
                </section>

                {/* Organism Components */}
                <section className="mb-12">
                    <h2 className="text-3xl font-semibold mb-6 text-gray-800 dark:text-gray-100">
                        Organism Components
                    </h2>

                    {/* Code Viewer */}
                    <div className="mb-8">
                        <div className="flex justify-between items-center mb-4">
                            <h3 className="text-xl font-semibold text-gray-700 dark:text-gray-200">
                                Code Viewer (Monaco Editor)
                            </h3>
                            <button
                                onClick={() => setTheme(theme === 'vs-dark' ? 'light' : 'vs-dark')}
                                className="px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded-lg text-sm font-medium"
                            >
                                Toggle Theme
                            </button>
                        </div>
                        <CodeViewer
                            code={sampleCode}
                            language={Language.PYTHON}
                            highlightedLines={[5, 6, 7]}
                            theme={theme}
                            height={400}
                        />
                    </div>

                    {/* Call Graph Viewer */}
                    <div className="mb-8">
                        <h3 className="text-xl font-semibold mb-4 text-gray-700 dark:text-gray-200">
                            Call Graph Viewer (D3.js)
                        </h3>
                        <CallGraphViewer
                            nodes={sampleNodes}
                            edges={sampleEdges}
                            entryPoints={['index']}
                            height={400}
                        />
                    </div>
                </section>
            </div>
        </div>
    )
}
