import { Suspense } from 'react';
import Navbar from '@/components/Navbar';
import SearchHero from '@/components/SearchHero';
import FactGrid from '@/components/FactGrid';
import SemanticAnswer from '@/components/SemanticAnswer';
import { FactCheckResponse } from '@/types';

// Force dynamic rendering since we depend on searchParams
export const dynamic = 'force-dynamic';

async function getFacts(query?: string, lang: string = 'en'): Promise<FactCheckResponse> {
  const apiKey = process.env.GOOGLE_API_KEY;
  if (!apiKey) return { error: "API Key missing" };

  const baseUrl = "https://factchecktools.googleapis.com/v1alpha1/claims:search";
  const url = new URL(baseUrl);
  url.searchParams.append('key', apiKey);
  url.searchParams.append('languageCode', lang);
  url.searchParams.append('pageSize', '12'); // More initial items for grid
  if (query) {
    url.searchParams.append('query', query);
  }

  if (!query) {
    url.searchParams.append('query', lang === 'hi' ? 'वायरल' : 'viral');
  }

  try {
    const res = await fetch(url.toString(), { cache: 'no-store' }); // Ensure fresh data on refresh
    if (!res.ok) {
      console.error("API Error", res.status, await res.text());
      return { claims: [] };
    }
    return await res.json();
  } catch (e) {
    console.error("Fetch Error", e);
    return { claims: [] };
  }
}

export default async function Home({
  searchParams,
}: {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}) {
  const resolvedSearchParams = await searchParams;
  const query = typeof resolvedSearchParams.query === 'string' ? resolvedSearchParams.query : "";
  const lang = typeof resolvedSearchParams.lang === 'string' ? resolvedSearchParams.lang : "en";
  const data = await getFacts(query, lang);

  return (
    <main className="min-h-screen">
      <Navbar />

      <div className="pt-24 pb-12">
        <Suspense fallback={<div>Loading Search...</div>}>
          <SearchHero initialLang={lang} />
        </Suspense>
      </div>

      {query && data.claims && data.claims.length > 0 && (
        <SemanticAnswer query={query} claims={data.claims} lang={lang} />
      )}


      <div className="px-4 mb-4">
        <div className="max-w-7xl mx-auto flex items-center gap-4 mb-6">
          <h2 className="text-2xl font-serif font-bold text-white">
            {query
              ? (lang === 'hi' ? `"${query}" के परिणाम` : `Results for "${query}"`)
              : (lang === 'hi' ? "ट्रेंडिंग फैक्ट चेक" : "Trending / Viral Claims")}
          </h2>
          <div className="h-px flex-1 bg-white/10"></div>
        </div>
      </div>

      <Suspense fallback={<div className="text-center text-white">Loading Feed...</div>}>
        <FactGrid
          initialClaims={data.claims || []}
          initialNextPageToken={data.nextPageToken}
          query={query}
          lang={lang}
        />
      </Suspense>

    </main>
  );
}
