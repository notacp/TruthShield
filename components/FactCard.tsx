import { Claim } from '@/types';
import { ExternalLink, Calendar, CheckCircle, XCircle, AlertTriangle, HelpCircle, ImageIcon } from 'lucide-react';
import { useState, useEffect } from 'react';

interface FactCardProps {
    claim: Claim;
}

export default function FactCard({ claim }: FactCardProps) {
    const review = claim.claimReview?.[0];
    const rating = review?.textualRating?.toLowerCase() || 'unknown';
    const reviewUrl = review?.url;
    const [imageUrl, setImageUrl] = useState<string | null>(null);

    useEffect(() => {
        if (reviewUrl) {
            // Lazy fetch image
            fetch(`/api/metadata?url=${encodeURIComponent(reviewUrl)}`)
                .then(res => res.json())
                .then(data => {
                    if (data.imageUrl) setImageUrl(data.imageUrl);
                })
                .catch(err => console.error("Failed to load image", err));
        }
    }, [reviewUrl]);

    // Badge Logic
    let badgeColor = "bg-gray-600/20 text-gray-400 border-gray-600/50";
    let Icon = HelpCircle;

    if (rating.includes("true") && !rating.includes("partially")) {
        badgeColor = "bg-green-500/10 text-green-400 border-green-500/50";
        Icon = CheckCircle;
    } else if (rating.includes("false") || rating.includes("fake") || rating.includes("incorrect")) {
        badgeColor = "bg-red-500/10 text-red-400 border-red-500/50";
        Icon = XCircle;
    } else if (rating.includes("misleading") || rating.includes("partially")) {
        badgeColor = "bg-yellow-500/10 text-yellow-400 border-yellow-500/50";
        Icon = AlertTriangle;
    }

    const reviewDate = review?.reviewDate ? new Date(review.reviewDate).toLocaleDateString() : 'Unknown date';

    return (
        <div className="glass-panel rounded-xl overflow-hidden hover:border-primary/50 transition-all duration-300 group flex flex-col h-full">
            {/* Image Section */}
            <div className="relative h-48 w-full bg-slate-900/50 overflow-hidden">
                {imageUrl ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                        src={imageUrl}
                        alt="Claim thumbnail"
                        className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                    />
                ) : (
                    <div className="w-full h-full flex items-center justify-center text-gray-700">
                        <ImageIcon size={48} opacity={0.2} />
                    </div>
                )}

                {/* Badge Overlay */}
                <div className={`absolute top-3 right-3 px-3 py-1 rounded-full text-xs font-semibold border flex items-center gap-1.5 backdrop-blur-md shadow-lg ${badgeColor}`}>
                    <Icon size={14} />
                    <span className="uppercase tracking-wider">{review?.textualRating || "Unrated"}</span>
                </div>
            </div>

            <div className="p-6 flex flex-col flex-1">
                <div className="flex justify-between items-start mb-3">
                    <span className="text-xs text-gray-500 flex items-center gap-1">
                        <Calendar size={12} /> {reviewDate}
                    </span>
                </div>

                <h3 className="text-lg font-serif font-semibold text-gray-100 mb-3 leading-snug group-hover:text-primary transition-colors line-clamp-3">
                    {claim.text}
                </h3>

                <div className="mt-auto pt-4 border-t border-white/5 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <span className="text-sm text-gray-400 font-medium truncate max-w-[150px]">
                            {review?.publisher?.name || "Unknown Publisher"}
                        </span>
                    </div>

                    {review?.url && (
                        <a
                            href={review.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-primary hover:text-accent-gold transition-colors p-2 rounded-full hover:bg-white/5"
                        >
                            <ExternalLink size={18} />
                        </a>
                    )}
                </div>
            </div>
        </div>
    );
}
