"use client";

import React, { useEffect, useRef, useState } from "react";
import Link from "next/link";
import Footer from "@/app/components/Footer";
import ImageCarousel from "@/app/components/ImageCarousel";

export default function RecipeDetail({ params: promiseParams }) {
    const scrollableRef = useRef(null); // Reference for the scrollable container
    const [recipe, setRecipe] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchRecipe = async () => {
            setLoading(true);
            try {
                const { id } = await promiseParams; // Unwrap the params promise
                const res = await fetch(`http://localhost:8844/recipes/${id}`, {
                    cache: "no-store",
                });

                if (!res.ok) {
                    throw new Error("Recipe not found");
                }

                const data = await res.json();
                setRecipe(data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchRecipe();
    }, [promiseParams]);

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen text-white">
                <p className="text-lg">Loading recipe details...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen text-white">
                <p className="text-lg">Error: {error}</p>
                <Link
                    href="/recipes"
                    className="mt-4 bg-red-500 hover:bg-red-700 text-white px-4 py-2 rounded"
                >
                    Go Back
                </Link>
            </div>
        );
    }

    const imgLinks = recipe.img_links
        ? recipe.img_links.split(/, |,/).map((link) => link.trim())
        : [];

    const ingredientsList = recipe.ingredients
        ? recipe.ingredients.split(/;;/).map((ingredient) => ingredient.trim())
        : [];

    return (
        <div
            className="h-screen"
            style={{
                background: "linear-gradient(to bottom, rgba(31, 41, 55, 0.9), rgba(17, 24, 39, 0.9))",
            }}
        >
            {/* Scrollable Content */}
            <div ref={scrollableRef} className="h-full overflow-y-auto p-8 scrollbar">
                {/* Breadcrumb Navigation */}
                <nav className="bg-gray-800 text-white py-3 px-6 rounded-lg mb-4">
                    <Link href="/recipes" className="hover:underline">
                        Recipes
                    </Link>
                    <span className="mx-2">/</span>
                    <span>{recipe.title}</span>
                </nav>

                {/* Recipe Detail Content */}
                <div className="max-w-5xl mx-auto bg-gray-700 text-white p-8 rounded-lg">
                    <h1 className="text-3xl font-bold mb-4">{recipe.title}</h1>

                    {imgLinks.length > 0 && <ImageCarousel imgLinks={imgLinks} />}

                    <div className="flex flex-wrap space-x-6 mb-6">
                        <div className="flex items-center space-x-2">
                            <img src="/pin-48.svg" alt="Cuisine" className="w-6 h-6" />
                            <span className="text-lg">{recipe.cuisine}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                            {recipe.diet_type === "Gluten-Free" && (
                                <img
                                    src="/gluten-free-seeklogo.svg"
                                    alt="Gluten-Free"
                                    className="w-6 h-6"
                                />
                            )}
                            {recipe.diet_type === "Vegetarian" && (
                                <img
                                    src="/vegetarian.svg"
                                    alt="Vegetarian"
                                    className="w-6 h-6"
                                />
                            )}
                            {recipe.diet_type === "Non-Vegetarian" && (
                                <img
                                    src="/non-vegetarian.svg"
                                    alt="Non-Vegetarian"
                                    className="w-6 h-6"
                                />
                            )}
                            <span className="text-lg">{recipe.diet_type}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                            <img src="/clock.svg" alt="Time to Cook" className="w-6 h-6" />
                            <span className="text-lg">{recipe.time_to_eat} min</span>
                        </div>
                    </div>

                    <div className="bg-gray-800 p-6 rounded-lg mb-6">
                        <h2 className="text-2xl font-semibold mb-4">Instructions</h2>
                        <p className="text-gray-300 whitespace-pre-line">{recipe.instructions}</p>
                    </div>

                    <div className="bg-gray-800 p-6 rounded-lg mb-6">
                        <h2 className="text-2xl font-semibold mb-4">Additional Information</h2>
                        <ul className="list-disc list-inside space-y-2 text-gray-300">
                            {recipe.servings && <li><strong>Servings:</strong> {recipe.servings}</li>}
                            {recipe.prep_time && <li><strong>Preparation Time:</strong> {recipe.prep_time} min</li>}
                            {recipe.time_to_eat && <li><strong>Cooking Time:</strong> {recipe.time_to_eat} min</li>}
                        </ul>
                    </div>

                    <div className="bg-gray-800 p-6 rounded-lg mb-6">
                        <h2 className="text-2xl font-semibold mb-4">Ingredients</h2>
                        <ul className="list-disc list-inside space-y-2 text-gray-300">
                            {ingredientsList.map((ingredient, index) => (
                                <li key={index}>{ingredient}</li>
                            ))}
                        </ul>
                    </div>

                    <div className="text-center">
                        <Link
                            href="/recipes"
                            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                        >
                            Back to Recipes
                        </Link>
                    </div>
                </div>

                {/* Empty Space for Footer Padding */}
                <div style={{ height: "64px" }}></div>
            </div>

            <Footer />
        </div>
    );
}
