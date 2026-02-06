/**
 * Project list page
 */
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useProjects } from '../../hooks/useApi';

export function ProjectList() {
    const [languageFilter, setLanguageFilter] = useState<string>('');
    const [difficultyFilter, setDifficultyFilter] = useState<number | undefined>();

    const { data: projects, isLoading, error } = useProjects({
        language: languageFilter || undefined,
        difficulty: difficultyFilter,
    });

    const languages = ['python', 'javascript', 'go', 'rust'];
    const difficulties = [1, 2, 3, 4, 5];

    if (error) {
        return (
            <div className="p-6">
                <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 text-red-300">
                    Failed to load projects. Please try again.
                </div>
            </div>
        );
    }

    return (
        <div className="p-6 space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white">Projects</h1>
                    <p className="text-slate-400 mt-1">Explore real-world codebases and learn by doing</p>
                </div>
                <Link
                    to="/projects/create"
                    className="inline-flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-medium rounded-xl transition-all duration-200 shadow-lg shadow-purple-500/25 hover:shadow-purple-500/40"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M12 5v14M5 12h14" />
                    </svg>
                    Add Project
                </Link>
            </div>

            {/* Filters */}
            <div className="flex flex-wrap gap-3">
                {/* Language Filter */}
                <div className="flex items-center space-x-2">
                    <span className="text-sm text-slate-400">Language:</span>
                    <div className="flex space-x-1">
                        <button
                            onClick={() => setLanguageFilter('')}
                            className={`px-3 py-1.5 text-sm rounded-lg transition ${!languageFilter
                                ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
                                : 'text-slate-400 hover:text-white hover:bg-slate-800'
                                }`}
                        >
                            All
                        </button>
                        {languages.map((lang) => (
                            <button
                                key={lang}
                                onClick={() => setLanguageFilter(lang)}
                                className={`px-3 py-1.5 text-sm rounded-lg transition capitalize ${languageFilter === lang
                                    ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
                                    : 'text-slate-400 hover:text-white hover:bg-slate-800'
                                    }`}
                            >
                                {lang}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Difficulty Filter */}
                <div className="flex items-center space-x-2">
                    <span className="text-sm text-slate-400">Difficulty:</span>
                    <div className="flex space-x-1">
                        <button
                            onClick={() => setDifficultyFilter(undefined)}
                            className={`px-3 py-1.5 text-sm rounded-lg transition ${difficultyFilter === undefined
                                ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
                                : 'text-slate-400 hover:text-white hover:bg-slate-800'
                                }`}
                        >
                            All
                        </button>
                        {difficulties.map((diff) => (
                            <button
                                key={diff}
                                onClick={() => setDifficultyFilter(diff)}
                                className={`px-3 py-1.5 text-sm rounded-lg transition ${difficultyFilter === diff
                                    ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
                                    : 'text-slate-400 hover:text-white hover:bg-slate-800'
                                    }`}
                            >
                                {'⭐'.repeat(diff)}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Projects Grid */}
            {isLoading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {[1, 2, 3, 4, 5, 6].map((i) => (
                        <div key={i} className="bg-slate-800/50 rounded-xl p-5 animate-pulse">
                            <div className="h-4 bg-slate-700 rounded w-1/3 mb-3" />
                            <div className="h-6 bg-slate-700 rounded w-2/3 mb-2" />
                            <div className="h-4 bg-slate-700 rounded w-full mb-4" />
                            <div className="h-4 bg-slate-700 rounded w-1/4" />
                        </div>
                    ))}
                </div>
            ) : projects?.items.length === 0 ? (
                <div className="text-center py-12">
                    <p className="text-slate-400">No projects found matching your filters.</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {projects?.items.map((project) => (
                        <Link
                            key={project.id}
                            to={`/projects/${project.id}`}
                            className="bg-slate-800/50 rounded-xl p-5 border border-slate-700/50 hover:border-purple-500/50 transition-all duration-300 group"
                        >
                            {/* Tags */}
                            <div className="flex items-center space-x-2 mb-3">
                                <span className="px-2 py-0.5 text-xs bg-purple-500/20 text-purple-300 rounded capitalize">
                                    {project.language}
                                </span>
                                <span className="text-sm text-yellow-400">
                                    {'⭐'.repeat(project.difficulty)}
                                </span>
                                {project.analysis_status === 'completed' && (
                                    <span className="px-2 py-0.5 text-xs bg-green-500/20 text-green-300 rounded">
                                        Ready
                                    </span>
                                )}
                            </div>

                            {/* Title */}
                            <h3 className="text-lg font-semibold text-white group-hover:text-purple-300 transition">
                                {project.name}
                            </h3>

                            {/* Description */}
                            <p className="text-sm text-slate-400 mt-2 line-clamp-2">
                                {project.description || 'Explore this codebase to understand how it works'}
                            </p>

                            {/* Meta */}
                            <div className="flex items-center justify-between mt-4 pt-4 border-t border-slate-700/50">
                                <span className="text-sm text-slate-500">
                                    {project.total_levels} levels
                                </span>
                                <span className="text-sm text-purple-400 group-hover:translate-x-1 transition-transform">
                                    Start learning →
                                </span>
                            </div>
                        </Link>
                    ))}
                </div>
            )}

            {/* Pagination */}
            {projects && projects.total_pages > 1 && (
                <div className="flex justify-center space-x-2">
                    {Array.from({ length: projects.total_pages }, (_, i) => (
                        <button
                            key={i}
                            className={`w-8 h-8 rounded-lg text-sm transition ${projects.page === i + 1
                                ? 'bg-purple-500 text-white'
                                : 'text-slate-400 hover:bg-slate-800'
                                }`}
                        >
                            {i + 1}
                        </button>
                    ))}
                </div>
            )}
        </div>
    );
}
