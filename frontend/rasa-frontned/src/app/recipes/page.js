"use client";

import React, { useEffect, useRef, useState } from "react";
import RecipeCard from "../components/RecipeCard"; // Ensure this points to your RecipeCard file
import Footer from "../components/Footer"; // Ensure this points to your Footer file

export default function Recipes() {
    const [recipes, setRecipes] = useState([]);
    const [cuisines, setCuisines] = useState([]);
    const [dietTypes, setDietTypes] = useState([]);
    const [selectedCuisine, setSelectedCuisine] = useState("");
    const [selectedDietType, setSelectedDietType] = useState("");
    const [page, setPage] = useState(1);
    const [totalRecipes, setTotalRecipes] = useState(0);
    const [loading, setLoading] = useState(true);
    const [minLoadingTime, setMinLoadingTime] = useState(false);
    const scrollableRef = useRef(null); // Reference to the scrollable container
    const limit = 9;

    useEffect(() => {
        // Fetch dropdown options on component mount
        Promise.all([
            fetch("http://localhost:8844/cuisines")
                .then((res) => res.json())
                .then((data) => setCuisines(data || [])),
            fetch("http://localhost:8844/diet_types")
                .then((res) => res.json())
                .then((data) => setDietTypes(data || [])),
        ]).catch((err) => console.error("Failed to fetch dropdown options:", err));
    }, []);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            setMinLoadingTime(true);

            const queryParams = new URLSearchParams({
                page,
                limit,
                ...(selectedCuisine && { cuisine: selectedCuisine }),
                ...(selectedDietType && { diet_type: selectedDietType }),
            });

            try {
                const res = await fetch(`http://localhost:8844/recipes?${queryParams}`);
                const data = await res.json();
                setTotalRecipes(data.total_recipes);
                setRecipes((prev) =>
                    page === 1 ? data.recipes : [...prev, ...data.recipes]
                );
            } catch (err) {
                console.error("Failed to fetch recipes:", err);
            } finally {
                setTimeout(() => setMinLoadingTime(false), 500); // Enforce 0.5s loading
                setLoading(false);
            }
        };

        fetchData();
    }, [selectedCuisine, selectedDietType, page]);

    const handleLoadMore = () => {
        setPage((prevPage) => prevPage + 1);
    };

    const handleFilterChange = () => {
        setRecipes([]); // Remove cards immediately
        setPage(1); // Reset page
    };

    const resetFilters = () => {
        setSelectedCuisine("");
        setSelectedDietType("");
        handleFilterChange();
    };

    const scrollToTop = () => {
        if (scrollableRef.current) {
            scrollableRef.current.scrollTo({ top: 0, behavior: "smooth" });
        }
    };

    return (
        <div
            className="h-screen"
            style={{
                background: "linear-gradient(to bottom, rgba(31, 41, 55, 0.9), rgba(17, 24, 39, 0.9))",
            }}
        >
            {/* Scrollable Content */}
            <div ref={scrollableRef} className="h-full overflow-y-auto p-8 scrollbar">
                {/* Sticky Filter Bar */}
                <div
                    className={`p-4 mb-4 rounded-lg shadow-md flex justify-between items-center glassy-bar sticky-bar ${
                        loading || minLoadingTime ? "animate-glassy-bar" : ""
                    }`}
                >
                    {/* Filters */}
                    <div className="flex space-x-4 items-center">
                        {/* Cuisine Dropdown */}
                        <div className="flex items-center space-x-2">
                            <label htmlFor="cuisine" className="text-white text-sm">
                                Cuisine:
                            </label>
                            <select
                                id="cuisine"
                                value={selectedCuisine}
                                onChange={(e) => {
                                    setSelectedCuisine(e.target.value);
                                    handleFilterChange();
                                }}
                                className="w-40 p-2 rounded bg-gray-800 text-white border border-gray-600"
                            >
                                <option value="">All Cuisines</option>
                                {cuisines.map((cuisine) => (
                                    <option key={cuisine} value={cuisine}>
                                        {cuisine}
                                    </option>
                                ))}
                            </select>
                        </div>
                        {/* Diet Type Dropdown */}
                        <div className="flex items-center space-x-2">
                            <label htmlFor="dietType" className="text-white text-sm">
                                Diet Type:
                            </label>
                            <select
                                id="dietType"
                                value={selectedDietType}
                                onChange={(e) => {
                                    setSelectedDietType(e.target.value);
                                    handleFilterChange();
                                }}
                                className="w-40 p-2 rounded bg-gray-800 text-white border border-gray-600"
                            >
                                <option value="">All Diet Types</option>
                                {dietTypes.map((dietType) => (
                                    <option key={dietType} value={dietType}>
                                        {dietType}
                                    </option>
                                ))}
                            </select>
                        </div>
                    </div>
                    {/* Scroll-to-Top Button */}
                    <button
                        onClick={scrollToTop}
                        className="bg-blue-500 hover:bg-blue-700 text-white px-4 py-2 rounded"
                    >
                        ↑
                    </button>
                </div>

                {/* Cards Grid */}
                {recipes.length > 0 ? (
                    <div
                        className="grid grid-cols-[repeat(auto-fit,minmax(350px,1fr))] gap-6"
                    >
                        {recipes.map((recipe, index) => (
                            <div
                                key={recipe.id}
                                className="opacity-0 animate-fade-in"
                                style={{
                                    animationDelay: `${
                                        index >= recipes.length - limit
                                            ? (index - (recipes.length - limit)) * 0.1
                                            : 0
                                    }s`,
                                }}
                            >
                                <RecipeCard recipe={recipe} />
                            </div>
                        ))}
                    </div>
                ) : loading ? (
                    <div className="flex flex-col items-center text-white mt-20">
                        <p className="text-lg">Loading, please wait...</p>
                    </div>
                ) : (
                    <div className="flex flex-col items-center text-white mt-20">
                        <p className="text-lg mb-4">No recipes found for the selected filters.</p>
                        <button
                            onClick={resetFilters}
                            className="bg-red-500 hover:bg-red-700 text-white px-6 py-3 rounded-lg"
                        >
                            Reset Filters
                        </button>
                    </div>
                )}

                {/* Load More Button */}
                {recipes.length > 0 && recipes.length < totalRecipes && (
                    <div className="flex justify-center mt-6">
                        <button
                            onClick={handleLoadMore}
                            className="bg-blue-500 hover:bg-blue-700 text-white py-2 px-4 rounded"
                        >
                            Load More
                        </button>
                    </div>
                )}
                {/* Footer */}
                <Footer />
                <div style={{height: '64px'}}></div>
            </div>
        </div>
    );
}
