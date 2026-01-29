'use client';

import { useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Search, Loader2 } from 'lucide-react';

export default function SearchHero() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const initialQuery = searchParams.get('query') || '';
    const [query, setQuery] = useState(initialQuery);
    const [isSearching, setIsSearching] = useState(false);

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        if (!query.trim()) return;

        setIsSearching(true);
        // Push new URL, page will refresh via Next.js
        router.push(`/?query=${encodeURIComponent(query)}`);
        // Minimal timeout to reset loading state if navigation is instant or to just show feedback
        setTimeout(() => setIsSearching(false), 1000);
    };

    return (
        <div className="relative w-full max-w-2xl mx-auto text-center py-20 px-4">
            {/* Abstract Background Decoration */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[120%] h-[120%] bg-blue-500/10 blur-[100px] rounded-full pointer-events-none" />

            <h1 className="relative text-5xl md:text-6xl font-serif font-bold text-white mb-6">
                Verify the <span className="text-primary italic">Unseen</span>
            </h1>
            <p className="relative text-lg text-gray-400 mb-10 max-w-lg mx-auto">
                TruthShield uses advanced fact-checking networks to validate claims in real-time.
            </p>

            <form onSubmit={handleSearch} className="relative group">
                <div className="absolute inset-0 bg-gradient-to-r from-primary to-accent-gold rounded-full blur opacity-25 group-hover:opacity-50 transition duration-500" />
                <div className="relative flex items-center bg-[#0f172a] border border-white/10 rounded-full p-2 shadow-2xl transition-all duration-300 focus-within:ring-2 focus-within:ring-primary/50 focus-within:border-primary">
                    <Search className="ml-4 text-gray-400" size={24} />
                    <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Search a claim (e.g., 'solar flares internet')"
                        className="flex-1 bg-transparent border-none outline-none text-white px-4 py-3 placeholder:text-gray-500 text-lg font-medium"
                    />
                    <button
                        type="submit"
                        disabled={isSearching}
                        className="bg-primary hover:bg-blue-600 text-white rounded-full px-8 py-3 font-semibold transition-all duration-300 disabled:opacity-70 disabled:cursor-not-allowed"
                    >
                        {isSearching ? <Loader2 className="animate-spin" /> : 'Check'}
                    </button>
                </div>
            </form>
        </div>
    );
}
