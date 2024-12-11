"use client";

import Navbar from "./components/Navbar";
import Chatbot from "./components/Chatbot"; // Import Chatbot component
import "./globals.css";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

export default function RootLayout({ children }) {
    const pathname = usePathname();
    const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

    useEffect(() => {
        const handleMouseMove = (event) => {
            setMousePosition({
                x: event.clientX / window.innerWidth,
                y: event.clientY / window.innerHeight,
            });
        };
        window.addEventListener("mousemove", handleMouseMove);
        return () => window.removeEventListener("mousemove", handleMouseMove);
    }, []);

    return (
        <html lang="en">
        <body className="h-screen flex flex-col relative overflow-hidden">
        {/* Dynamic Background */}
        <div
            className="absolute inset-0 pointer-events-none z-0"
            style={{
                background: `radial-gradient(circle at ${
                    mousePosition.x * 100
                }% ${mousePosition.y * 100}%, rgba(255, 255, 255, 0.2), rgba(0, 0, 0, 0.3))`,
                transition: "background-position 0.1s ease",
            }}
        />
        {/* Navbar Glow */}
        {pathname !== "/" && (
            <div
                className="absolute top-0 left-0 w-full h-16 pointer-events-none z-20"
                style={{
                    background: `radial-gradient(circle at ${
                        mousePosition.x * 100
                    }% ${mousePosition.y * 100}%, rgba(255, 255, 255, 0.1), rgba(40, 40, 40, 0.4))`,
                    transition: "background-position 0.1s ease",
                }}
            />
        )}
        {/* Conditionally render Navbar */}
        {pathname !== "/" && <Navbar />}
        <main className="relative z-10 flex-grow">{children}</main>
        {/* Chatbot Window */}
        {pathname !== "/" && <Chatbot />}
        </body>
        </html>
    );
}
