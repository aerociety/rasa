"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";

function RecipeCard({ recipe }) {
    const [currentImageIndex, setCurrentImageIndex] = useState(0);
    const imgLinks = recipe.img_links
        ? recipe.img_links.split(/, |,/).map((link) => link.trim())
        : [];

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
        <div className="bg-gray-700 text-white rounded-lg shadow-md overflow-hidden flex flex-col h-full">
            {/* Image Carousel */}
            <div className="relative bg-black h-60">
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
                <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 flex space-x-2">
                    {imgLinks.map((_, index) => (
                        <div
                            key={index}
                            className={`w-2 h-2 rounded-full ${
                                index === currentImageIndex
                                    ? "bg-white"
                                    : "bg-gray-400"
                            }`}
                        />
                    ))}
                </div>
            </div>
            {/* Highlighted Info Row */}
            <div className="p-4 flex items-center space-x-4 bg-gray-600">
                {/* Time to Cook */}
                <div className="flex items-center space-x-2">
                    <img src="/clock.svg" alt="Time to Cook" className="w-5 h-5" />
                    <span>{recipe.time_to_eat} min</span>
                </div>
                {/* Diet Type */}
                <div className="flex items-center space-x-2">
                    {recipe.diet_type === "Gluten-Free" && (
                        <img
                            src="/gluten-free-seeklogo.svg"
                            alt="Gluten-Free"
                            className="w-5 h-5"
                        />
                    )}
                    {recipe.diet_type === "Vegetarian" && (
                        <img
                            src="/vegetarian.svg"
                            alt="Vegetarian"
                            className="w-5 h-5"
                        />
                    )}
                    {recipe.diet_type === "Non-Vegetarian" && (
                        <img
                            src="/non-vegetarian.svg"
                            alt="Non-Vegetarian"
                            className="w-5 h-5"
                        />
                    )}
                    <span>{recipe.diet_type}</span>
                </div>
                {/* Cuisine */}
                <div className="flex items-center space-x-2">
                    <img src="/pin-48.svg" alt="Cuisine" className="w-5 h-5" />
                    <span>{recipe.cuisine}</span>
                </div>
            </div>
            {/* Recipe Info */}
            <div className="p-4 flex-grow flex flex-col">
                <h2 className="text-xl font-bold mb-2 line-clamp-2">{recipe.title}</h2>
                <p className="text-sm mt-2 line-clamp-4 relative">
                    {recipe.instructions}
                    <span className="absolute bottom-0 left-0 w-full h-6 bg-gradient-to-t from-gray-700 to-transparent" />
                </p>
            </div>
            {/* Centered View Button */}
            <div className="p-4 flex justify-center">
                <Link
                    href={`/recipes/${recipe.id}/`}
                    className="inline-block bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                >
                    View Recipe
                </Link>
            </div>
        </div>
    )
}

export default RecipeCard;
