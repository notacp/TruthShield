import { Suspense } from 'react';
import Navbar from '@/components/Navbar';
import SearchHero from '@/components/SearchHero';
import FactGrid from '@/components/FactGrid';
import { FactCheckResponse } from '@/types';

// Force dynamic rendering since we depend on searchParams
export const dynamic = 'force-dynamic';

async function getFacts(query?: string): Promise<FactCheckResponse> {
  const apiKey = process.env.GOOGLE_API_KEY;
  if (!apiKey) return { error: "API Key missing" };

  const baseUrl = "https://factchecktools.googleapis.com/v1alpha1/claims:search";
  const url = new URL(baseUrl);
  url.searchParams.append('key', apiKey);
  url.searchParams.append('languageCode', 'en');
  url.searchParams.append('pageSize', '12'); // More initial items for grid
  if (query) {
    url.searchParams.append('query', query);
  }
  // If no query, we might want a default search or just recent claims if API supports it (it usually requires query or reviewPublisherSiteFilter)
  // The Streamlit app used "India" as default. Let's use a generic term like "news" or "world" or "latest" if empty, 
  // OR check if empty query is allowed. API docs say 'query' is optional if 'reviewPublisherSiteFilter' is present.
  // Let's default to "news" for discovery if empty.
  if (!query) {
    url.searchParams.append('query', 'viral');
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
  const data = await getFacts(query);

  return (
    <main className="min-h-screen">
      <Navbar />

      <div className="pt-24 pb-12">
        <Suspense fallback={<div>Loading Search...</div>}>
          <SearchHero />
        </Suspense>
      </div>

      <div className="px-4 mb-4">
        <div className="max-w-7xl mx-auto flex items-center gap-4 mb-6">
          <h2 className="text-2xl font-serif font-bold text-white">
            {query ? `Results for "${query}"` : "Trending / Viral Claims"}
          </h2>
          <div className="h-px flex-1 bg-white/10"></div>
        </div>
      </div>

      <Suspense fallback={<div className="text-center text-white">Loading Feed...</div>}>
        <FactGrid
          initialClaims={data.claims || []}
          initialNextPageToken={data.nextPageToken}
          query={query}
        />
      </Suspense>
    </main>
  );
}
