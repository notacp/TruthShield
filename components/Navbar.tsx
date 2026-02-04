'use client';

import { useState } from 'react';
import Link from 'next/link';
import { ShieldCheck, Menu, X } from 'lucide-react';

export default function Navbar() {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <nav className="fixed top-0 w-full z-50 border-b border-white/10 bg-[#050a14]/80 backdrop-blur-md">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    {/* Logo Section */}
                    <Link href="/" className="flex items-center space-x-2 group z-50" onClick={() => setIsOpen(false)}>
                        <ShieldCheck className="h-8 w-8 text-primary group-hover:text-accent-gold transition-colors duration-300" />
                        <span className="font-serif text-xl font-bold tracking-tight text-white">
                            Truth<span className="text-primary group-hover:text-accent-gold transition-colors duration-300">Shield</span>
                        </span>
                    </Link>

                    {/* Desktop Navigation */}
                    <div className="hidden md:block">
                        <div className="ml-10 flex items-baseline space-x-4">
                            <Link href="/about" className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors">
                                About
                            </Link>
                        </div>
                    </div>

                    {/* Mobile Menu Button */}
                    <div className="md:hidden flex items-center z-50">
                        <button
                            onClick={() => setIsOpen(!isOpen)}
                            className="text-gray-300 hover:text-white focus:outline-none p-2"
                            aria-label="Toggle menu"
                        >
                            {isOpen ? <X size={24} /> : <Menu size={24} />}
                        </button>
                    </div>
                </div>
            </div>

            {/* Mobile Navigation Menu */}
            <div
                className={`fixed inset-0 bg-[#050a14] z-40 transition-transform duration-300 ease-in-out md:hidden flex flex-col items-center justify-center space-y-8 ${isOpen ? 'translate-x-0' : 'translate-x-full'
                    }`}
            >
                <Link
                    href="/about"
                    className="text-2xl font-serif text-gray-300 hover:text-white transition-colors"
                    onClick={() => setIsOpen(false)}
                >
                    About
                </Link>
            </div>
        </nav>
    );
}
