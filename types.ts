export interface Publisher {
    name?: string;
    site?: string;
}

export interface ClaimReview {
    publisher?: Publisher;
    url?: string;
    title?: string;
    reviewDate?: string;
    textualRating?: string;
    languageCode?: string;
}

export interface Claim {
    text: string;
    claimant?: string;
    claimDate?: string;
    claimReview?: ClaimReview[];
}

export interface FactCheckResponse {
    claims?: Claim[];
    nextPageToken?: string;
    error?: string;
}
