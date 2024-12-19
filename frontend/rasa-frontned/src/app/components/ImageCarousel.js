"use client";

import React, {useEffect, useState} from "react";

export default function ImageCarousel({ imgLinks }) {
    const [currentImageIndex, setCurrentImageIndex] = useState(0);

    useEffect(() => {
        if (imgLinks.length > 1) {
            const interval = setInterval(() => {
                setCurrentImageIndex((prevIndex) =>
                    (prevIndex + 1) % imgLinks.length
                );
            }, Math.random() * (10000 - 5000) + 5000); // Random interval between 5s to 10s

            return () => clearInterval(interval);
        }
    }, [imgLinks]);

    return (
        <div className="relative bg-black h-80 rounded-lg overflow-hidden mb-6">
            {imgLinks.map((img, index) => (
                <img
                    key={index}
                    src={img}
                    alt={`Recipe Image ${index + 1}`}
                    className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-700 ${
                        index === currentImageIndex ? "opacity-100" : "opacity-0"
                    }`}
                />
            ))}
            {/* Image Indicators */}
            {imgLinks.length > 1 && (
                <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex space-x-2">
                    {imgLinks.map((_, index) => (
                        <div
                            key={index}
                            className={`w-3 h-3 rounded-full cursor-pointer ${
                                index === currentImageIndex
                                    ? "bg-white"
                                    : "bg-gray-400"
                            }`}
                            onClick={() => setCurrentImageIndex(index)}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}