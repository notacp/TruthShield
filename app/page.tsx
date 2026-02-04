import { Suspense } from 'react';
import Navbar from '@/components/Navbar';
import SearchHero from '@/components/SearchHero';
import FactGrid from '@/components/FactGrid';
import SemanticAnswer from '@/components/SemanticAnswer';
import { FactCheckResponse } from '@/types';
import { GoogleGenerativeAI } from '@google/generative-ai';

// Force dynamic rendering since we depend on searchParams
export const dynamic = 'force-dynamic';

async function refineQuery(rawQuery: string): Promise<string> {
  if (!process.env.GEMINI_API_KEY) return rawQuery;

  // Simple heuristic: If it's short, it's likely already a keyword search
  if (rawQuery.split(' ').length < 4) return rawQuery;

  try {
    const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
    const model = genAI.getGenerativeModel({ model: "gemini-3-flash-preview" });

    const prompt = `
      Extract the core subject/keywords from this user question for a fact-check database search.
      User Question: "${rawQuery}"
      
      Rules:
      1. Remove "when", "what", "how", "latest", "recent", "news", etc.
      2. Keep proper nouns and key actions.
      3. Return ONLY the keywords.
      
      Example: "When was the latest pakistan attack" -> "Pakistan attack"
      Example: "Is it true that Modi won" -> "Modi won"
    `;

    const result = await model.generateContent(prompt);
    const refined = result.response.text().trim();
    console.log(`Query Refined: "${rawQuery}" -> "${refined}"`); // Debug log
    return refined;
  } catch (error) {
    console.error("Refinement failed:", error);
    return rawQuery;
  }
}

async function getFacts(query?: string, lang: string = 'en'): Promise<FactCheckResponse> {
  const apiKey = process.env.GOOGLE_API_KEY;
  if (!apiKey) return { error: "API Key missing" };

  const baseUrl = "https://factchecktools.googleapis.com/v1alpha1/claims:search";
  const url = new URL(baseUrl);
  url.searchParams.append('key', apiKey);
  url.searchParams.append('languageCode', lang);
  url.searchParams.append('pageSize', '12'); // More initial items for grid

  let effectiveQuery = query;

  if (query) {
    effectiveQuery = await refineQuery(query);
    url.searchParams.append('query', effectiveQuery);
  }

  if (!query) {
    url.searchParams.append('query', lang === 'hi' ? 'वायरल' : 'viral');
  }

  const maxRetries = 3;
  let attempt = 0;

  while (attempt < maxRetries) {
    try {
      const res = await fetch(url.toString(), { cache: 'no-store' }); // Ensure fresh data on refresh

      if (res.ok) {
        return await res.json();
      }

      // If rate limited or server error, wait and retry
      if (res.status === 429 || res.status >= 500) {
        console.warn(`API Error ${res.status}. Retrying attempt ${attempt + 1}/${maxRetries}...`);
        attempt++;
        await new Promise(resolve => setTimeout(resolve, 1000 * attempt)); // Exponential backoffish
        continue;
      }

      console.error("API Error", res.status, await res.text());
      return { claims: [] };

    } catch (e) {
      console.error("Fetch Error", e);
      attempt++;
      if (attempt >= maxRetries) return { claims: [] };
      await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
    }
  }

  return { claims: [] };
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
