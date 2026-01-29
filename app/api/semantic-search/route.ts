import { GoogleGenerativeAI } from "@google/generative-ai";
import { NextResponse } from "next/server";
import { Claim } from "@/types";

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY || "");

export async function POST(request: Request) {
    const { query, claims, lang } = await request.json();

    if (!process.env.GEMINI_API_KEY) {
        return NextResponse.json({ error: "Gemini API Key missing" }, { status: 500 });
    }

    if (!query || !claims || !Array.isArray(claims)) {
        return NextResponse.json({ error: "Invalid request data" }, { status: 400 });
    }

    const model = genAI.getGenerativeModel({ model: "gemini-3-flash-preview" });

    const claimsContext = claims.map((c: Claim, i: number) => {
        const review = c.claimReview?.[0];
        return `[Source ${i + 1}] Claim: ${c.text}. Rating: ${review?.textualRating || 'Unknown'}. Publisher: ${review?.publisher?.name || 'Unknown'}.`;
    }).join("\n");

    const prompt = `
    You are TruthShield AI, a professional fact-checking assistant. 
    User Query: "${query}"
    
    Here are the relevant fact-check records found:
    ${claimsContext || "No specific fact-check records found for this query."}

    INSTRUCTIONS:
    1. Analyze the provided records to answer the user's query.
    2. Respond in the same language as the User Query (if Hindi, respond in Hindi).
    3. If the records clearly confirm or debunk the claim in the query, state the verdict (True, False, or Misleading).
    4. If there are no relevant records or the information is insufficient, state "No claims around this found" (in the relevant language).
    5. Only provide a verdict if you are highly confident based strictly on the provided records.
    6. ALWAYS cite your sources using [Source 1], [Source 2], etc.
    7. Keep the response concise, authoritative, and professional.
    8. Format the output in Markdown.

    ${lang === 'hi' ? 'IMPORTANT: Please provide the "Verdict", "Summary", and "Sources" headers in Hindi.' : ''}

    Response structure:
    - Verdict (Primary status)
    - Summary (Clear explanation)
    - Sources (List of cited sources)
  `;


    try {
        const result = await model.generateContent(prompt);
        const response = await result.response;
        const text = response.text();
        return NextResponse.json({ answer: text });
    } catch (error) {
        console.error("Gemini Error:", error);
        return NextResponse.json({ error: "Failed to generate semantic answer" }, { status: 500 });
    }
}
