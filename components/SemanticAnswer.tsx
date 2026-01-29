'use client';

import { useState, useEffect, useMemo } from 'react';
import { Claim } from '@/types';
import { Sparkles, Loader2, AlertCircle, ShieldCheck } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface SemanticAnswerProps {
    query: string;
    claims: Claim[];
    lang?: string;
}

export default function SemanticAnswer({ query, claims, lang = 'en' }: SemanticAnswerProps) {
    const [answer, setAnswer] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!query || claims.length === 0) {
            setAnswer(null);
            return;
        }

        const fetchAnswer = async () => {
            setIsLoading(true);
            setError(null);
            try {
                const res = await fetch('/api/semantic-search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query, claims, lang }),
                });
                const data = await res.json();
                if (data.error) throw new Error(data.error);
                setAnswer(data.answer);
            } catch (err: any) {
                setError(err.message);
            } finally {
                setIsLoading(false);
            }
        };

        fetchAnswer();
    }, [query, claims]);

    const linkedAnswer = useMemo(() => {
        if (!answer) return null;
        // Regex to find [Source X] patterns
        return answer.replace(/\[Source (\d+)\]/g, (match, number) => {
            const idx = parseInt(number) - 1;
            const url = claims[idx]?.claimReview?.[0]?.url;
            // Return markdown link format if URL exists, else return original match
            return url ? `[${match}](${url})` : match;
        });
    }, [answer, claims]);

    if (!query) return null;

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-12">
            <div className="relative overflow-hidden glass-panel rounded-2xl border-primary/20 shadow-2xl">
                <div className="absolute top-0 left-0 w-2 h-full bg-gradient-to-b from-primary to-accent-gold" />

                <div className="p-6 md:p-8">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="bg-primary/20 p-2 rounded-lg">
                            <ShieldCheck className="text-primary" size={24} />
                        </div>
                        <h3 className="text-xl font-serif font-bold text-white flex items-center gap-2">
                            TruthShield <span className="text-primary italic">Intelligence</span>
                        </h3>
                        {isLoading && <Loader2 className="animate-spin text-primary ml-auto" size={20} />}
                    </div>

                    {isLoading ? (
                        <div className="flex flex-col gap-4 animate-pulse">
                            <div className="h-4 bg-white/5 rounded w-3/4"></div>
                            <div className="h-4 bg-white/5 rounded w-full"></div>
                            <div className="h-4 bg-white/5 rounded w-5/6"></div>
                        </div>
                    ) : error ? (
                        <div className="flex items-center gap-3 text-red-400 bg-red-400/10 p-4 rounded-xl border border-red-400/20">
                            <AlertCircle size={20} />
                            <p>Unable to generate semantic analysis. {error.includes('Key') ? 'Please check GEMINI_API_KEY.' : ''}</p>
                        </div>
                    ) : answer ? (
                        <div className="markdown-content">
                            <ReactMarkdown
                                remarkPlugins={[remarkGfm]}
                                components={{
                                    h1: ({ ...props }) => <h1 className="text-2xl font-serif font-bold text-white mb-4" {...props} />,
                                    h2: ({ ...props }) => <h2 className="text-xl font-serif font-bold text-white mb-3 mt-6" {...props} />,
                                    h3: ({ ...props }) => <h3 className="text-lg font-serif font-bold text-primary mb-2 mt-4 uppercase tracking-wider border-b border-primary/20 pb-1" {...props} />,
                                    p: ({ ...props }) => <p className="text-gray-200 leading-relaxed mb-4" {...props} />,
                                    ul: ({ ...props }) => <ul className="list-disc list-inside space-y-2 mb-4 text-gray-300 ml-4" {...props} />,
                                    ol: ({ ...props }) => <ol className="list-decimal list-inside space-y-2 mb-4 text-gray-300 ml-4" {...props} />,
                                    li: ({ ...props }) => <li className="marker:text-primary pl-1" {...props} />,
                                    strong: ({ ...props }) => <strong className="text-white font-bold" {...props} />,
                                    blockquote: ({ ...props }) => <blockquote className="border-l-4 border-primary/40 pl-4 italic my-4 text-gray-400" {...props} />,
                                    code: ({ ...props }) => <code className="bg-white/10 px-1.5 py-0.5 rounded text-accent-gold font-mono text-sm" {...props} />,
                                    a: ({ ...props }) => (
                                        <a
                                            className="text-primary hover:text-accent-gold underline underline-offset-2 transition-colors duration-200"
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            {...props}
                                        />
                                    ),
                                }}
                            >
                                {linkedAnswer || ''}
                            </ReactMarkdown>
                        </div>
                    ) : null}
                </div>

                {/* Decorative elements */}
                <div className="absolute -bottom-10 -right-10 w-40 h-40 bg-primary/5 blur-[80px] rounded-full pointer-events-none" />
            </div>
        </div>
    );
}
