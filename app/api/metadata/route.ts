import { NextResponse } from 'next/server';
import * as cheerio from 'cheerio';

export async function GET(request: Request) {
    const { searchParams } = new URL(request.url);
    const targetUrl = searchParams.get('url');

    if (!targetUrl) {
        return NextResponse.json({ error: "Missing URL parameter" }, { status: 400 });
    }

    try {
        const response = await fetch(targetUrl, {
            headers: { 'User-Agent': 'Mozilla/5.0 (compatible; TruthShieldBot/1.0;)' },
            next: { revalidate: 86400 }
        });

        if (!response.ok) {
            return NextResponse.json({ error: "Failed to fetch page" }, { status: response.status });
        }

        const html = await response.text();
        const $ = cheerio.load(html);

        let imageUrl: string | undefined =
            $('meta[property="og:image"]').attr('content') ||
            $('meta[name="twitter:image"]').attr('content') ||
            $('link[rel="image_src"]').attr('href') ||
            $('img').first().attr('src');

        if (imageUrl && !imageUrl.startsWith('http')) {
            try {
                imageUrl = new URL(imageUrl, targetUrl).toString();
            } catch {
                imageUrl = undefined;
            }
        }

        return NextResponse.json({ imageUrl: imageUrl ?? null });

    } catch (error) {
        return NextResponse.json({ error: "Scraping failed", details: String(error) }, { status: 500 });
    }
}
