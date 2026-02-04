'use client';

import { useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Search, Loader2 } from 'lucide-react';

interface SearchHeroProps {
    initialLang?: string;
}

export default function SearchHero({ initialLang = 'en' }: SearchHeroProps) {
    const router = useRouter();
    const searchParams = useSearchParams();
    const initialQuery = searchParams.get('query') || '';
    const [query, setQuery] = useState(initialQuery);
    const [lang, setLang] = useState(initialLang);
    const [isSearching, setIsSearching] = useState(false);

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();

        setIsSearching(true);
        // Push new URL with language parameter
        router.push(`/?query=${encodeURIComponent(query)}&lang=${lang}`);
        setTimeout(() => setIsSearching(false), 800);
    };

    const placeholders: Record<string, string> = {
        en: "Search a claim (e.g., 'solar flares internet')",
        hi: "कोई दावा खोजें (उदा. 'कोरोना वायरस वैक्सीन')"
    };

    const buttonText: Record<string, string> = {
        en: "Check",
        hi: "जांचें"
    };

    return (
        <div className="relative w-full max-w-2xl mx-auto text-center py-20 px-4">
            {/* Abstract Background Decoration */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[120%] h-[120%] bg-blue-500/10 blur-[100px] rounded-full pointer-events-none" />

            <h1 className="relative text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-serif font-bold text-white mb-6 group cursor-default leading-tight">
                Verify the <span className="text-primary italic group-hover:text-accent-gold transition-colors duration-300">Unseen</span>
            </h1>
            <p className="relative text-lg text-gray-400 mb-10 max-w-lg mx-auto">
                TruthShield uses advanced fact-checking networks to validate claims in real-time.
            </p>

            <div className="flex justify-center gap-2 mb-6 relative z-10">
                <button
                    onClick={() => { setLang('en'); router.push(`/?query=${query}&lang=en`); }}
                    className={`px-4 py-1.5 rounded-full text-sm font-medium transition-all ${lang === 'en' ? 'bg-primary text-white shadow-lg shadow-primary/20' : 'bg-white/5 text-gray-400 hover:bg-white/10'}`}
                >
                    English
                </button>
                <button
                    onClick={() => { setLang('hi'); router.push(`/?query=${query}&lang=hi`); }}
                    className={`px-4 py-1.5 rounded-full text-sm font-medium transition-all ${lang === 'hi' ? 'bg-primary text-white shadow-lg shadow-primary/20' : 'bg-white/5 text-gray-400 hover:bg-white/10'}`}
                >
                    हिन्दी
                </button>
            </div>

            <form onSubmit={handleSearch} className="relative group">
                <div className="absolute inset-0 bg-gradient-to-r from-primary to-accent-gold rounded-full blur opacity-25 group-hover:opacity-50 transition duration-500" />
                <div className="relative flex flex-col sm:flex-row items-center bg-[#0f172a] border border-white/10 rounded-3xl sm:rounded-full p-2 shadow-2xl transition-all duration-300 focus-within:ring-2 focus-within:ring-primary/50 focus-within:border-primary gap-2 sm:gap-0">
                    <Search className="hidden sm:block ml-4 text-gray-400 min-w-[24px]" size={24} />
                    <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder={placeholders[lang]}
                        className="w-full sm:flex-1 bg-transparent border-none outline-none text-white px-4 py-3 placeholder:text-gray-500 text-base sm:text-lg font-medium text-center sm:text-left"
                    />
                    <button
                        type="submit"
                        disabled={isSearching}
                        className="w-full sm:w-auto bg-primary hover:bg-blue-600 text-white rounded-xl sm:rounded-full px-8 py-3 font-semibold transition-all duration-300 disabled:opacity-70 disabled:cursor-not-allowed whitespace-nowrap"
                    >
                        {isSearching ? <Loader2 className="animate-spin mx-auto" /> : buttonText[lang]}
                    </button>
                </div>
            </form>

        </div>
    );
}
