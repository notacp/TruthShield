import { NextResponse } from 'next/server';

const API_ENDPOINT = "https://factchecktools.googleapis.com/v1alpha1/claims:search";

export async function GET(request: Request) {
    const { searchParams } = new URL(request.url);
    const query = searchParams.get('query');
    const pageToken = searchParams.get('pageToken');
    const languageCode = searchParams.get('languageCode') || 'en';
    const pageSize = searchParams.get('pageSize') || '10';

    const apiKey = process.env.GOOGLE_API_KEY;

    if (!apiKey) {
        return NextResponse.json({ error: "Server misconfiguration: API Key missing" }, { status: 500 });
    }

    // Construct URL with params
    const url = new URL(API_ENDPOINT);
    url.searchParams.append('key', apiKey);
    if (query) url.searchParams.append('query', query);
    url.searchParams.append('languageCode', languageCode);
    url.searchParams.append('pageSize', pageSize);
    if (pageToken) url.searchParams.append('pageToken', pageToken);

    try {
        const res = await fetch(url.toString(), { next: { revalidate: 3600 } }); // Cache for 1 hour like before

        if (!res.ok) {
            const errorData = await res.json().catch(() => ({}));
            return NextResponse.json({ error: "Upstream API Error", details: errorData }, { status: res.status });
        }

        const data = await res.json();
        return NextResponse.json(data);

    } catch (error) {
        return NextResponse.json({ error: "Internal Server Error", details: String(error) }, { status: 500 });
    }
}
