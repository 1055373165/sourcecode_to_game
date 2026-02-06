/**
 * ProjectDetail - Shows project levels and learning progress
 */
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api } from '../../api/client';

interface LevelInfo {
    id: string;
    name: string;
    description: string | null;
    difficulty: number;
    entry_function: string | null;
    code_snippet: string | null;
    xp_reward: number;
    estimated_time: number;
    challenges_count: number;
    is_completed: boolean;
    score: number;
}

interface ProjectLevelsResponse {
    project_id: string;
    project_name: string;
    total_levels: number;
    levels: LevelInfo[];
}

export default function ProjectDetail() {
    const { projectId } = useParams<{ projectId: string }>();
    const navigate = useNavigate();

    const { data, isLoading, error } = useQuery<ProjectLevelsResponse>({
        queryKey: ['project-levels', projectId],
        queryFn: () => api.getProjectLevels(projectId!),
        enabled: !!projectId
    });

    const getDifficultyLabel = (difficulty: number) => {
        const labels = ['', 'Tutorial', 'Basic', 'Intermediate', 'Advanced', 'Expert'];
        return labels[difficulty] || 'Unknown';
    };

    const getDifficultyColor = (difficulty: number) => {
        const colors = [
            '',
            'text-green-400',   // Tutorial
            'text-blue-400',    // Basic
            'text-yellow-400',  // Intermediate
            'text-orange-400',  // Advanced
            'text-red-400'      // Expert
        ];
        return colors[difficulty] || 'text-gray-400';
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-purple-500 border-t-transparent"></div>
            </div>
        );
    }

    if (error || !data) {
        return (
            <div className="text-center py-12">
                <div className="text-red-400 text-xl mb-4">Failed to load project</div>
                <button
                    onClick={() => navigate('/projects')}
                    className="text-purple-400 hover:text-purple-300"
                >
                    ← Back to Projects
                </button>
            </div>
        );
    }

    const completedLevels = data.levels.filter(l => l.is_completed).length;
    const progressPercent = data.total_levels > 0 ? (completedLevels / data.total_levels) * 100 : 0;

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <Link
                        to="/projects"
                        className="text-purple-400 hover:text-purple-300 mb-2 inline-block"
                    >
                        ← Back to Projects
                    </Link>
                    <h1 className="text-3xl font-bold text-white">{data.project_name}</h1>
                    <p className="text-gray-400 mt-1">
                        {data.total_levels} levels • {completedLevels} completed
                    </p>
                </div>
            </div>

            {/* Progress Bar */}
            <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700/50">
                <div className="flex items-center justify-between mb-3">
                    <span className="text-gray-300">Your Progress</span>
                    <span className="text-purple-400 font-semibold">{progressPercent.toFixed(0)}%</span>
                </div>
                <div className="h-3 bg-gray-700 rounded-full overflow-hidden">
                    <div
                        className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-500"
                        style={{ width: `${progressPercent}%` }}
                    />
                </div>
            </div>

            {/* Levels Grid */}
            <div className="grid gap-4">
                {data.levels.map((level, index) => (
                    <Link
                        key={level.id}
                        to={`/levels/${level.id}`}
                        className={`block p-6 rounded-xl border transition-all duration-300 hover:scale-[1.01] 
                            ${level.is_completed
                                ? 'bg-green-900/20 border-green-600/30 hover:border-green-500/50'
                                : 'bg-gray-800/50 border-gray-700/50 hover:border-purple-500/50'
                            }`}
                    >
                        <div className="flex items-start justify-between">
                            <div className="flex-1">
                                <div className="flex items-center gap-3 mb-2">
                                    <span className="text-gray-500 text-sm">Level {index + 1}</span>
                                    <span className={`text-sm ${getDifficultyColor(level.difficulty)}`}>
                                        {getDifficultyLabel(level.difficulty)}
                                    </span>
                                    {level.is_completed && (
                                        <span className="bg-green-600/20 text-green-400 text-xs px-2 py-0.5 rounded">
                                            ✓ Completed
                                        </span>
                                    )}
                                </div>

                                <h3 className="text-xl font-semibold text-white mb-2">
                                    {level.name}
                                </h3>

                                {level.description && (
                                    <p className="text-gray-400 text-sm mb-3 line-clamp-2">
                                        {level.description}
                                    </p>
                                )}

                                <div className="flex items-center gap-4 text-sm text-gray-500">
                                    <span>🎯 {level.challenges_count} challenges</span>
                                    <span>⏱ {level.estimated_time} min</span>
                                    <span>⭐ {level.xp_reward} XP</span>
                                </div>
                            </div>

                            <div className="ml-4">
                                <div className={`w-10 h-10 rounded-full flex items-center justify-center 
                                    ${level.is_completed
                                        ? 'bg-green-600'
                                        : 'bg-purple-600/20 border border-purple-500/30'
                                    }`}
                                >
                                    {level.is_completed ? (
                                        <span className="text-white">✓</span>
                                    ) : (
                                        <span className="text-purple-400">→</span>
                                    )}
                                </div>
                            </div>
                        </div>
                    </Link>
                ))}
            </div>

            {data.levels.length === 0 && (
                <div className="text-center py-12 text-gray-400">
                    <div className="text-4xl mb-4">📚</div>
                    <p>No levels available yet. The project may still be analyzing.</p>
                </div>
            )}
        </div>
    );
}
