// RecipeSuggestionCard.js
"use client";

import React from "react";
import Link from "next/link";

export default function RecipeSuggestionCard({ recipe }) {
    // Use first image if available
    const imgLinks = recipe.img_links
        ? recipe.img_links.split(/, |,/).map((link) => link.trim())
        : [];
    const imageUrl = imgLinks[0] || "/placeholder-image.png";

    return (
        <Link
            href={`/recipes/${recipe.id}/`}
            className="group block"
        >
            <div className="flex bg-gray-800 text-white rounded-lg p-2 mb-2 shadow-md transition-all duration-300 transform group-hover:scale-105 group-hover:bg-gray-700 group-hover:shadow-lg cursor-pointer">
                {/* Image Section */}
                <div className="w-20 h-20 overflow-hidden rounded-lg flex-shrink-0 mr-2">
                    <img src={imageUrl} alt={recipe.title} className="object-cover w-full h-full" />
                </div>
                {/* Text Content */}
                <div className="flex-grow flex flex-col justify-between">
                    <h3 className="font-bold text-sm group-hover:text-blue-400 transition-colors duration-300">
                        {recipe.title}
                    </h3>
                    <div className="text-xs text-gray-300 flex items-center space-x-2 mt-1">
                        <span>{recipe.cuisine}</span>
                        <span>|</span>
                        <span>{recipe.diet_type}</span>
                        <span>|</span>
                        <span>{recipe.time_to_eat} min</span>
                    </div>
                </div>
            </div>
        </Link>
    );
}
