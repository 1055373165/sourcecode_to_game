import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { Button } from '../atoms/Button';

import { Github, Loader2, CheckCircle, AlertCircle, Code } from 'lucide-react';

interface CreateProjectForm {
    githubUrl: string;
    name: string;
    language: string;
}

interface AnalysisProgress {
    project_id: string;
    status: string;
    progress: number;
    message: string;
    total_levels: number;
}

export function CreateProject() {
    const navigate = useNavigate();
    const [form, setForm] = useState<CreateProjectForm>({
        githubUrl: '',
        name: '',
        language: 'python'
    });
    const [error, setError] = useState('');
    const [projectId, setProjectId] = useState<string | null>(null);
    const [progress, setProgress] = useState<AnalysisProgress | null>(null);
    const [isPolling, setIsPolling] = useState(false);

    // Create project mutation
    const createMutation = useMutation({
        mutationFn: async () => {
            const params = new URLSearchParams({
                github_url: form.githubUrl,
                name: form.name,
                ...(form.language && { language: form.language })
            });
            const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/projects?${params}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                }
            });
            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.error?.message || 'Failed to create project');
            }
            return response.json();
        },
        onSuccess: (data) => {
            setProjectId(data.id);
            startPolling(data.id);
        },
        onError: (err: Error) => {
            setError(err.message);
        }
    });

    // Poll for analysis progress
    const startPolling = async (id: string) => {
        setIsPolling(true);
        const poll = async () => {
            try {
                const response = await fetch(
                    `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/projects/${id}/progress`,
                    {
                        headers: {
                            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                        }
                    }
                );
                if (response.ok) {
                    const data: AnalysisProgress = await response.json();
                    setProgress(data);

                    if (data.status === 'completed') {
                        setIsPolling(false);
                        // Navigate to project after short delay
                        setTimeout(() => navigate(`/projects/${id}`), 1500);
                    } else if (data.status === 'failed') {
                        setIsPolling(false);
                        setError(data.message || 'Analysis failed');
                    } else {
                        // Continue polling
                        setTimeout(poll, 2000);
                    }
                }
            } catch (err) {
                console.error('Polling error:', err);
                setTimeout(poll, 3000);
            }
        };
        poll();
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (!form.githubUrl.trim()) {
            setError('Please enter a GitHub URL');
            return;
        }
        if (!form.name.trim()) {
            setError('Please enter a project name');
            return;
        }

        createMutation.mutate();
    };

    const isLoading = createMutation.isPending || isPolling;

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 py-12 px-4">
            <div className="max-w-2xl mx-auto">
                {/* Header */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl mb-4">
                        <Github className="w-8 h-8 text-white" />
                    </div>
                    <h1 className="text-3xl font-bold text-white mb-2">
                        Add New Project
                    </h1>
                    <p className="text-slate-400">
                        Enter a GitHub repository URL to generate learning levels
                    </p>
                </div>

                {/* Form Card */}
                <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-8">
                    {!projectId ? (
                        <form onSubmit={handleSubmit} className="space-y-6">
                            {/* Error Alert */}
                            {error && (
                                <div className="flex items-center gap-3 p-4 bg-red-500/20 border border-red-500/50 rounded-xl text-red-300">
                                    <AlertCircle className="w-5 h-5 flex-shrink-0" />
                                    <span>{error}</span>
                                </div>
                            )}

                            {/* GitHub URL */}
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-2">
                                    GitHub Repository URL *
                                </label>
                                <div className="relative">
                                    <Github className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                                    <input
                                        type="url"
                                        value={form.githubUrl}
                                        onChange={(e) => setForm({ ...form, githubUrl: e.target.value })}
                                        placeholder="https://github.com/owner/repo"
                                        className="w-full pl-12 pr-4 py-3 bg-slate-900/50 border border-slate-600 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                                    />
                                </div>
                                <p className="mt-2 text-xs text-slate-500">
                                    Example: https://github.com/pallets/flask
                                </p>
                            </div>

                            {/* Project Name */}
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-2">
                                    Project Name *
                                </label>
                                <input
                                    type="text"
                                    value={form.name}
                                    onChange={(e) => setForm({ ...form, name: e.target.value })}
                                    placeholder="My Learning Project"
                                    className="w-full px-4 py-3 bg-slate-900/50 border border-slate-600 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                                />
                            </div>

                            {/* Language Selection */}
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-2">
                                    Programming Language
                                </label>
                                <div className="grid grid-cols-2 gap-3">
                                    {['python', 'golang'].map((lang) => (
                                        <button
                                            key={lang}
                                            type="button"
                                            onClick={() => setForm({ ...form, language: lang })}
                                            className={`flex items-center justify-center gap-2 p-4 rounded-xl border transition-all ${form.language === lang
                                                ? 'border-purple-500 bg-purple-500/20 text-purple-300'
                                                : 'border-slate-600 bg-slate-900/30 text-slate-400 hover:border-slate-500'
                                                }`}
                                        >
                                            <Code className="w-5 h-5" />
                                            <span className="capitalize font-medium">{lang}</span>
                                        </button>
                                    ))}
                                </div>
                                <p className="mt-2 text-xs text-slate-500">
                                    Leave unselected to auto-detect from repository
                                </p>
                            </div>

                            {/* Submit Button */}
                            <Button
                                type="submit"
                                disabled={isLoading}
                                className="w-full py-4 text-lg font-semibold"
                            >
                                {createMutation.isPending ? (
                                    <>
                                        <Loader2 className="w-5 h-5 animate-spin mr-2" />
                                        Creating Project...
                                    </>
                                ) : (
                                    <>
                                        <Github className="w-5 h-5 mr-2" />
                                        Create Project
                                    </>
                                )}
                            </Button>
                        </form>
                    ) : (
                        /* Progress Display */
                        <div className="text-center py-8">
                            <div className="mb-6">
                                {progress?.status === 'completed' ? (
                                    <CheckCircle className="w-16 h-16 text-green-500 mx-auto" />
                                ) : (
                                    <Loader2 className="w-16 h-16 text-purple-500 mx-auto animate-spin" />
                                )}
                            </div>

                            <h2 className="text-xl font-semibold text-white mb-2">
                                {progress?.status === 'completed'
                                    ? 'Analysis Complete!'
                                    : 'Analyzing Repository...'}
                            </h2>

                            <p className="text-slate-400 mb-6">
                                {progress?.message || 'Starting analysis...'}
                            </p>

                            {/* Progress Bar */}
                            <div className="w-full bg-slate-700 rounded-full h-3 mb-4">
                                <div
                                    className="bg-gradient-to-r from-purple-500 to-pink-500 h-3 rounded-full transition-all duration-500"
                                    style={{ width: `${progress?.progress || 0}%` }}
                                />
                            </div>

                            <p className="text-sm text-slate-500">
                                {progress?.progress || 0}% complete
                            </p>

                            {progress?.status === 'completed' && progress.total_levels > 0 && (
                                <p className="mt-4 text-green-400">
                                    Generated {progress.total_levels} learning levels!
                                </p>
                            )}
                        </div>
                    )}
                </div>

                {/* Tips */}
                <div className="mt-6 p-4 bg-slate-800/30 border border-slate-700 rounded-xl">
                    <h3 className="text-sm font-medium text-slate-400 mb-2">💡 Tips</h3>
                    <ul className="text-xs text-slate-500 space-y-1">
                        <li>• Public repositories work best - private repos require additional setup</li>
                        <li>• Smaller repositories (under 100MB) are processed faster</li>
                        <li>• Python and Go projects have the best support currently</li>
                    </ul>
                </div>
            </div>
        </div>
    );
}
