"use client";

import React from "react";
import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";

export default function Navbar() {
    const pathname = usePathname();

    return (
        <nav className="bg-gradient-to-r from-gray-800 to-gray-900 text-white p-4 shadow-lg">
            <div className="flex items-center justify-between px-6 max-w-screen-2xl mx-auto">
                {/* Logo */}
                <div className="flex items-center">
                    <Image
                        src="/burger-svgrepo-com.svg"
                        alt="Logo"
                        width={32}
                        height={32}
                        className="mr-2"
                    />
                    <span className="text-lg font-bold">RCPY</span>
                </div>

                {/* Links */}
                <div className="flex space-x-6">
                    <Link
                        href="/"
                        className={`${
                            pathname === "/" ? "border-b-2 border-white" : ""
                        } hover:border-b-2 hover:border-white pb-1 transition duration-300`}
                    >
                        Home
                    </Link>
                    <Link
                        href="/recipes"
                        className={`${
                            pathname === "/recipes" ? "border-b-2 border-white" : ""
                        } hover:border-b-2 hover:border-white pb-1 transition duration-300`}
                    >
                        Recipes
                    </Link>
                    <Link
                        href="/about"
                        className={`${
                            pathname === "/about" ? "border-b-2 border-white" : ""
                        } hover:border-b-2 hover:border-white pb-1 transition duration-300`}
                    >
                        About
                    </Link>
                </div>
            </div>
        </nav>
    );
}
