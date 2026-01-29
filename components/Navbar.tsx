import Link from 'next/link';
import { ShieldCheck } from 'lucide-react';

export default function Navbar() {
    return (
        <nav className="fixed top-0 w-full z-50 border-b border-white/10 bg-[#050a14]/80 backdrop-blur-md">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    <Link href="/" className="flex items-center space-x-2 group">
                        <ShieldCheck className="h-8 w-8 text-primary group-hover:text-accent-gold transition-colors duration-300" />
                        <span className="font-serif text-xl font-bold tracking-tight text-white">
                            Truth<span className="text-primary group-hover:text-accent-gold transition-colors duration-300">Shield</span>
                        </span>
                    </Link>

                    <div className="hidden md:block">
                        <div className="ml-10 flex items-baseline space-x-4">
                            <Link href="/" className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors">
                                Home
                            </Link>
                            <Link href="/about" className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors">
                                About
                            </Link>
                        </div>
                    </div>
                </div>
            </div>
        </nav>
    );
}
