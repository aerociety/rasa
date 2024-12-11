"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import "tailwindcss/tailwind.css";

export default function Home() {
    const [isCardVisible, setIsCardVisible] = useState(false);
    const [userName, setUserName] = useState("");
    const router = useRouter();
    const [scale, setScale] = useState(1);

    useEffect(() => {
        const calculateScale = () => {
            const windowAspect = window.innerWidth / window.innerHeight;
            const videoAspect = 16 / 9;
            if (windowAspect > videoAspect) {
                // Wider than 16:9
                setScale(windowAspect / videoAspect);
            } else {
                // Taller than 16:9
                setScale(videoAspect / windowAspect);
            }
        };

        calculateScale();
        window.addEventListener("resize", calculateScale);

        return () => window.removeEventListener("resize", calculateScale);
    }, []);

    const handleGoClick = () => {
        if (userName.trim()) {
            router.push("/recipes");
        }
    };

    return (
        <div
            className="relative h-screen w-screen overflow-hidden bg-black"
            onClick={() => setIsCardVisible(true)} // Show card on click
        >
            {/* Background Video */}
            <div className="absolute inset-0">
                <iframe
                    className="absolute inset-0 w-full h-full object-cover"
                    style={{
                        transform: `scale(${scale})`, // Dynamically calculated scale
                    }}
                    src="https://www.youtube.com/embed/0Fs-4GiNxQ8?autoplay=1&controls=0&modestbranding=1&start=10&rel=0&showinfo=0&loop=1&mute=1&iv_load_policy=3&vq=hd1440"
                    title="Cinematic Background Video"
                    frameBorder="0"
                    allow="autoplay; fullscreen"
                ></iframe>
            </div>

            {/* Overlay */}
            <div
                className={`absolute inset-0 transition-all duration-700 ${
                    isCardVisible ? "bg-black bg-opacity-60 blur-lg" : "bg-transparent"
                }`}
            ></div>

            {/* Center Content */}
            {!isCardVisible && (
                <div className="absolute inset-0 flex items-center justify-center text-center">
                    <h1 className="text-white text-4xl sm:text-6xl font-bold tracking-widest">
                        Are You Ready for a New <br /> Cooking Adventure? <br />
                        <span className="text-lg sm:text-xl font-normal mt-4">
                            (Just click anywhere to begin)
                        </span>
                    </h1>
                </div>
            )}

            {/* Glassy Card */}
            {isCardVisible && (
                <div className="absolute inset-0 flex items-center justify-center">
                    <div
                        className="p-8 rounded-2xl border border-white/30 backdrop-blur-md"
                        style={{
                            background: "rgba(255, 255, 255, 0.11)",
                            boxShadow: "0 4px 30px rgba(0, 0, 0, 0.1)",
                            borderRadius: "16px",
                            backdropFilter: "blur(7.1px)",
                            WebkitBackdropFilter: "blur(7.1px)",
                            border: "1px solid rgba(255, 255, 255, 0.35)",
                        }}
                    >
                        <button
                            className="absolute top-4 right-4 text-white font-bold text-xl"
                            onClick={(e) => {
                                e.stopPropagation(); // Prevent background click from firing
                                setIsCardVisible(false);
                            }}
                        >
                            ✖
                        </button>
                        <h2 className="text-2xl font-bold text-white mb-4">
                            Enter Your Name
                        </h2>
                        <input
                            type="text"
                            placeholder="Your Name"
                            value={userName}
                            onChange={(e) => setUserName(e.target.value)}
                            className="w-full border border-gray-300 rounded-lg p-3 text-lg mb-4 focus:outline-none focus:ring-2 focus:ring-red-400"
                        />
                        <button
                            onClick={handleGoClick}
                            className="w-full bg-red-600 text-white py-3 rounded-lg font-semibold text-lg hover:bg-red-700 transition-all"
                        >
                            Cook It Up!
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
