"use client";

import React, { useState, useRef, useEffect } from "react";
import RecipeSuggestionCard from "@/app/components/RecipeSuggestionCard";

export default function Chatbot() {
    const [isExpanded, setIsExpanded] = useState(false);
    const [messages, setMessages] = useState([]);
    const [currentMessage, setCurrentMessage] = useState("");
    const [isAnimating, setIsAnimating] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const chatContentRef = useRef(null);

    const handleSendMessage = async () => {
        if (currentMessage.trim()) {
            setMessages((prev) => [...prev, { user: true, text: currentMessage }]);
            const userMessage = currentMessage;
            setCurrentMessage("");

            setIsAnimating(true);
            setIsLoading(true);

            try {
                const response = await fetch("http://localhost:5005/webhooks/rest/webhook", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ sender: "user", message: userMessage }),
                });
                const data = await response.json();

                const newMessages = [];
                for (let d of data) {
                    if (d.custom && d.custom.recipes) {
                        newMessages.push({ user: false, recipes: d.custom.recipes });
                    } else if (d.text) {
                        newMessages.push({ user: false, text: d.text });
                    }
                }

                setMessages((prev) => [...prev, ...newMessages]);
            } catch (error) {
                console.error("Failed to connect to RASA:", error);
                setMessages((prev) => [
                    ...prev,
                    { user: false, text: "Failed to connect to the bot. Please try again later." },
                ]);
            } finally {
                setIsAnimating(false);
                setIsLoading(false);
            }
        }
    };

    useEffect(() => {
        if (chatContentRef.current) {
            chatContentRef.current.scrollTop = chatContentRef.current.scrollHeight;
        }
    }, [messages]);

    useEffect(() => {
        if (isExpanded && chatContentRef.current) {
            chatContentRef.current.scrollTop = chatContentRef.current.scrollHeight;
        }
    }, [isExpanded]);

    return (
        <div
            className={`fixed bottom-4 right-4 z-50 transition-all duration-300 ${
                isExpanded ? "w-96 h-[30rem]" : "w-48 h-14"
            }`}
        >
            <div
                className={`rounded-lg shadow-lg overflow-hidden flex flex-col glassy-chatbot ${
                    isExpanded ? "h-full" : "h-14 w-48"
                }`}
            >
                {isExpanded && (
                    <div
                        className={`text-white flex items-center justify-between px-4 py-3 chatbot-header ${
                            isAnimating ? "animate-top-bar" : ""
                        }`}
                    >
                        <span className="font-semibold">
                            {isLoading ? "Typing..." : "Recipe Chatbot"}
                        </span>
                        <button
                            onClick={() => setIsExpanded(false)}
                            className="text-white hover:text-red-500 text-lg"
                        >
                            ✖
                        </button>
                    </div>
                )}

                {isExpanded ? (
                    <div className="flex-grow flex flex-col min-h-0">
                        <div
                            ref={chatContentRef}
                            className="flex-grow overflow-y-auto mb-4 p-4 scrollbar"
                        >
                            {messages.map((msg, index) => {
                                if (msg.recipes) {
                                    return (
                                        <div key={index} className="mb-2 text-left">
                                            {msg.recipes.map((recipe, i) => (
                                                <RecipeSuggestionCard key={i} recipe={recipe} />
                                            ))}
                                        </div>
                                    );
                                } else {
                                    return (
                                        <div
                                            key={index}
                                            className={`mb-2 ${
                                                msg.user ? "text-right" : "text-left"
                                            }`}
                                        >
                                            <span
                                                className={`inline-block px-3 py-2 rounded-lg ${
                                                    msg.user
                                                        ? "bg-blue-500 text-white"
                                                        : "bg-gray-300 text-black"
                                                }`}
                                            >
                                                {msg.text}
                                            </span>
                                        </div>
                                    );
                                }
                            })}
                        </div>
                        <div className="flex items-center p-4">
                            <input
                                type="text"
                                value={currentMessage}
                                onChange={(e) => setCurrentMessage(e.target.value)}
                                onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
                                placeholder="Type a message..."
                                className="flex-grow bg-gray-800 text-white p-2 rounded-l-lg focus:outline-none border border-gray-600"
                            />
                            <button
                                onClick={handleSendMessage}
                                className="bg-blue-500 hover:bg-blue-700 text-white px-4 py-2 rounded-r-lg"
                            >
                                ➤
                            </button>
                        </div>
                    </div>
                ) : (
                    <button
                        onClick={() => setIsExpanded(true)}
                        className="relative w-full h-full flex items-center justify-center rounded-lg shadow-md overflow-hidden group"
                    >
                        {/* Background Gradient */}
                        <div
                            className="absolute inset-0 bg-gradient-to-r from-blue-500 to-indigo-600
                            group-hover:from-blue-600 group-hover:to-indigo-700 transition-all
                            duration-500 ease-in-out"></div>
                        <span className="relative z-10 text-white font-semibold whitespace-nowrap">
                            RCPY Assistant
                        </span>
                    </button>
                )}
            </div>
        </div>
    );
}
