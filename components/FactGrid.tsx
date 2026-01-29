'use client';

import { useState, useEffect } from 'react';
import { Claim } from '@/types';
import FactCard from './FactCard';
import { Loader2 } from 'lucide-react';

interface FactGridProps {
    initialClaims: Claim[];
    initialNextPageToken?: string;
    query?: string;
}

export default function FactGrid({ initialClaims, initialNextPageToken, query }: FactGridProps) {
    const [claims, setClaims] = useState<Claim[]>(initialClaims);
    const [nextPageToken, setNextPageToken] = useState<string | undefined>(initialNextPageToken);
    const [isLoadingMore, setIsLoadingMore] = useState(false);

    // Reset state when initial claims change (i.e. new search from parent)
    useEffect(() => {
        setClaims(initialClaims);
        setNextPageToken(initialNextPageToken);
    }, [initialClaims, initialNextPageToken]);

    const loadMore = async () => {
        if (!nextPageToken) return;
        setIsLoadingMore(true);

        try {
            const params = new URLSearchParams();
            if (query) params.append('query', query);
            params.append('pageToken', nextPageToken);

            // Fetch via our internal API proxy to hide keys
            const res = await fetch(`/api/facts?${params.toString()}`);
            const data = await res.json();

            if (data.claims) {
                setClaims(prev => [...prev, ...data.claims]);
                setNextPageToken(data.nextPageToken);
            } else {
                setNextPageToken(undefined);
            }

        } catch (error) {
            console.error("Failed to load more", error);
        } finally {
            setIsLoadingMore(false);
        }
    };

    if (!claims || claims.length === 0) {
        return (
            <div className="text-center py-20">
                <h3 className="text-2xl font-serif text-gray-400">No results found.</h3>
                <p className="text-gray-500 mt-2">Try a different search term.</p>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-20">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {claims.map((claim, index) => (
                    // Using index as fallback key, ideally claim.text + date should be unique enough
                    <FactCard key={`${index}-${claim.text.substring(0, 10)}`} claim={claim} />
                ))}
            </div>

            {nextPageToken && (
                <div className="mt-12 text-center">
                    <button
                        onClick={loadMore}
                        disabled={isLoadingMore}
                        className="group relative inline-flex items-center justify-center px-8 py-3 text-base font-medium text-white bg-transparent border border-white/20 rounded-full hover:bg-white/5 transition-all duration-300"
                    >
                        {isLoadingMore ? (
                            <>
                                <Loader2 className="animate-spin mr-2" size={20} /> Loading...
                            </>
                        ) : (
                            <>
                                Load More Results
                                <span className="ml-2 group-hover:translate-y-0.5 transition-transform duration-300">↓</span>
                            </>
                        )}
                    </button>
                </div>
            )}
        </div>
    );
}
