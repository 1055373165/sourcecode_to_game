/**
 * Level view page - displays challenges and allows answers
 */
import { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useLevel, useSubmitLevel } from '../../hooks/useApi';
import { CodeViewer } from '../organisms/CodeViewer/CodeViewer';
import { Button } from '../atoms/Button';
import { Language } from '../../types/index';


export function LevelView() {
    const { levelId } = useParams<{ levelId: string }>();
    const navigate = useNavigate();
    const { data: level, isLoading, error } = useLevel(levelId || '');
    const submitMutation = useSubmitLevel();

    const [answers, setAnswers] = useState<Record<string, string>>({});
    const [currentChallenge, setCurrentChallenge] = useState(0);
    const [showHint, setShowHint] = useState(false);
    const [startTime] = useState(Date.now());
    const [result, setResult] = useState<{
        success: boolean;
        score: number;
        max_score: number;
        xp_earned: number;
    } | null>(null);

    if (isLoading) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <div className="animate-spin w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full" />
            </div>
        );
    }

    if (error || !level) {
        return (
            <div className="p-6">
                <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 text-red-300">
                    Failed to load level. <Link to="/projects" className="underline">Go back to projects</Link>
                </div>
            </div>
        );
    }

    const challenge = level.challenges[currentChallenge];
    const isLastChallenge = currentChallenge === level.challenges.length - 1;
    const allAnswered = level.challenges.every(c => answers[c.id]);

    const handleAnswer = (challengeId: string, answer: string) => {
        setAnswers(prev => ({ ...prev, [challengeId]: answer }));
    };

    const handleNext = () => {
        if (currentChallenge < level.challenges.length - 1) {
            setCurrentChallenge(prev => prev + 1);
            setShowHint(false);
        }
    };

    const handlePrev = () => {
        if (currentChallenge > 0) {
            setCurrentChallenge(prev => prev - 1);
            setShowHint(false);
        }
    };

    const handleSubmit = async () => {
        const timeSpent = Math.floor((Date.now() - startTime) / 1000);
        try {
            const res = await submitMutation.mutateAsync({
                levelId: level.id,
                answers,
                timeSpent,
            });
            setResult({
                success: res.level_completed,
                score: res.score,
                max_score: res.max_score,
                xp_earned: res.xp_earned,
            });
        } catch (err) {
            console.error('Submit error:', err);
        }
    };

    // Render result screen
    if (result) {
        const percentage = Math.round((result.score / result.max_score) * 100);
        return (
            <div className="p-6 max-w-2xl mx-auto">
                <div className="bg-slate-800/50 rounded-2xl p-8 border border-slate-700/50 text-center">
                    <div className="text-6xl mb-4">
                        {percentage >= 80 ? '🎉' : percentage >= 50 ? '👍' : '💪'}
                    </div>
                    <h2 className="text-2xl font-bold text-white mb-2">
                        {result.success ? 'Level Completed!' : 'Keep Practicing!'}
                    </h2>
                    <p className="text-slate-400 mb-6">{level.name}</p>

                    <div className="grid grid-cols-2 gap-4 mb-6">
                        <div className="bg-slate-900/50 rounded-xl p-4">
                            <p className="text-3xl font-bold text-white">{result.score}/{result.max_score}</p>
                            <p className="text-sm text-slate-400">Score</p>
                        </div>
                        <div className="bg-slate-900/50 rounded-xl p-4">
                            <p className="text-3xl font-bold text-purple-400">+{result.xp_earned}</p>
                            <p className="text-sm text-slate-400">XP Earned</p>
                        </div>
                    </div>

                    <div className="flex space-x-3 justify-center">
                        <Button
                            onClick={() => navigate(`/projects/${level.project_id}`)}
                            className="px-6 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg"
                        >
                            Back to Project
                        </Button>
                        <Button
                            onClick={() => navigate('/dashboard')}
                            className="px-6 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg"
                        >
                            Dashboard
                        </Button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="p-6 space-y-6">
            {/* Level Header */}
            <div className="flex items-center justify-between">
                <div>
                    <Link to={`/projects/${level.project_id}`} className="text-sm text-purple-400 hover:text-purple-300">
                        ← Back to Project
                    </Link>
                    <h1 className="text-2xl font-bold text-white mt-2">{level.name}</h1>
                    <p className="text-slate-400">{level.description}</p>
                </div>
                <div className="text-right">
                    <span className="text-sm text-slate-400">Reward</span>
                    <p className="text-lg font-bold text-purple-400">+{level.xp_reward} XP</p>
                </div>
            </div>

            {/* Code Snippet */}
            {level.code_snippet && (
                <div className="bg-slate-800/50 rounded-xl border border-slate-700/50 overflow-hidden">
                    <div className="px-4 py-2 bg-slate-900/50 border-b border-slate-700/50">
                        <span className="text-sm text-slate-400">Code to analyze</span>
                    </div>
                    <CodeViewer
                        code={level.code_snippet}
                        language={Language.PYTHON}
                        readOnly
                    />
                </div>
            )}

            {/* Challenge Progress */}
            <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                    {level.challenges.map((c, i) => (
                        <button
                            key={c.id}
                            onClick={() => setCurrentChallenge(i)}
                            className={`w-8 h-8 rounded-full text-sm font-medium transition ${i === currentChallenge
                                ? 'bg-purple-500 text-white'
                                : answers[c.id]
                                    ? 'bg-green-500/20 text-green-300 border border-green-500/30'
                                    : 'bg-slate-700 text-slate-400'
                                }`}
                        >
                            {i + 1}
                        </button>
                    ))}
                </div>
                <span className="text-sm text-slate-400">
                    Challenge {currentChallenge + 1} of {level.challenges.length}
                </span>
            </div>

            {/* Current Challenge */}
            {challenge && (
                <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700/50">
                    <div className="flex items-center justify-between mb-4">
                        <span className="px-2 py-1 text-xs bg-purple-500/20 text-purple-300 rounded capitalize">
                            {challenge.type.replace('_', ' ')}
                        </span>
                        <span className="text-sm text-slate-400">{challenge.points} points</span>
                    </div>

                    <h3 className="text-lg font-medium text-white mb-4">
                        {(challenge.question as any).text || 'Answer the question below'}
                    </h3>

                    {/* Multiple Choice */}
                    {challenge.type === 'multiple_choice' && (challenge.question as any).options && (
                        <div className="space-y-2">
                            {((challenge.question as any).options as string[]).map((option, i) => (
                                <button
                                    key={i}
                                    onClick={() => handleAnswer(challenge.id, option[0])}
                                    className={`w-full text-left px-4 py-3 rounded-lg border transition ${answers[challenge.id] === option[0]
                                        ? 'bg-purple-500/20 border-purple-500/50 text-white'
                                        : 'bg-slate-900/50 border-slate-700 text-slate-300 hover:border-slate-600'
                                        }`}
                                >
                                    {option}
                                </button>
                            ))}
                        </div>
                    )}

                    {/* Text Input */}
                    {(challenge.type === 'code_tracing' || challenge.type === 'fill_blank') && (
                        <input
                            type="text"
                            value={answers[challenge.id] || ''}
                            onChange={(e) => handleAnswer(challenge.id, e.target.value)}
                            className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
                            placeholder="Type your answer..."
                        />
                    )}

                    {/* Code Completion */}
                    {challenge.type === 'code_completion' && (
                        <textarea
                            value={answers[challenge.id] || ''}
                            onChange={(e) => handleAnswer(challenge.id, e.target.value)}
                            className="w-full h-32 px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500 font-mono text-sm"
                            placeholder="Write your code..."
                        />
                    )}

                    {/* Hint */}
                    {challenge.hints && challenge.hints.length > 0 && (
                        <div className="mt-4">
                            {showHint ? (
                                <div className="p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
                                    <p className="text-sm text-yellow-300">💡 {challenge.hints[0]}</p>
                                </div>
                            ) : (
                                <button
                                    onClick={() => setShowHint(true)}
                                    className="text-sm text-slate-400 hover:text-yellow-300"
                                >
                                    Need a hint?
                                </button>
                            )}
                        </div>
                    )}
                </div>
            )}

            {/* Navigation */}
            <div className="flex items-center justify-between">
                <Button
                    onClick={handlePrev}
                    disabled={currentChallenge === 0}
                    className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg disabled:opacity-50"
                >
                    ← Previous
                </Button>

                {isLastChallenge ? (
                    <Button
                        onClick={handleSubmit}
                        disabled={!allAnswered || submitMutation.isPending}
                        className="px-6 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white rounded-lg disabled:opacity-50"
                    >
                        {submitMutation.isPending ? 'Submitting...' : 'Submit Answers'}
                    </Button>
                ) : (
                    <Button
                        onClick={handleNext}
                        className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg"
                    >
                        Next →
                    </Button>
                )}
            </div>
        </div>
    );
}
