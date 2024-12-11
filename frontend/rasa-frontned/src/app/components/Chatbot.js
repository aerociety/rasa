"use client";

import React, { useState } from "react";

export default function Chatbot() {
    const [isExpanded, setIsExpanded] = useState(false);
    const [messages, setMessages] = useState([]);
    const [currentMessage, setCurrentMessage] = useState("");
    const [isAnimating, setIsAnimating] = useState(false);

    const handleSendMessage = () => {
        if (currentMessage.trim()) {
            // Add user's message
            setMessages((prev) => [...prev, { user: true, text: currentMessage }]);
            setCurrentMessage("");

            // Trigger animation for the top bar
            setIsAnimating(true);
            setTimeout(() => setIsAnimating(false), 5000); // Reset animation after 5 seconds

            // Add bot's fake response after 5 seconds
            setTimeout(() => {
                setMessages((prev) => [
                    ...prev,
                    { user: false, text: "Not Implemented Yet" },
                ]);
            }, 5000);
        }
    };

    return (
        <div
            className={`fixed bottom-4 right-4 z-50 transition-all duration-300 ${
                isExpanded ? "w-80 h-96" : "w-12 h-12"
            }`}
        >
            {/* Chatbot Container */}
            <div
                className={`rounded-lg shadow-lg overflow-hidden flex flex-col glassy-chatbot ${
                    isExpanded ? "h-full" : "h-12 w-12"
                }`}
            >
                {/* Top Bar */}
                {isExpanded && (
                    <div
                        className={`text-white flex items-center justify-between px-4 chatbot-header ${
                            isAnimating ? "animate-top-bar" : ""
                        }`}
                    >
                        <span className="font-semibold">Recipe Chatbot</span>
                        <button
                            onClick={() => setIsExpanded(false)}
                            className="text-white hover:text-red-500 text-lg"
                        >
                            ✖
                        </button>
                    </div>
                )}

                {/* Chatbot Content */}
                {isExpanded ? (
                    <div className="flex-grow p-4 flex flex-col">
                        {/* Messages */}
                        <div className="flex-grow overflow-y-auto mb-4">
                            {messages.map((msg, index) => (
                                <div
                                    key={index}
                                    className={`mb-2 ${
                                        msg.user
                                            ? "text-right text-white"
                                            : "text-left text-gray-300"
                                    }`}
                                >
                                    <span
                                        className={`inline-block px-3 py-2 rounded-lg ${
                                            msg.user
                                                ? "bg-blue-500"
                                                : "bg-gray-300 text-black"
                                        }`}
                                    >
                                        {msg.text}
                                    </span>
                                </div>
                            ))}
                        </div>
                        {/* Input Field */}
                        <div className="flex items-center">
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
                        className="w-full h-full bg-gray-800 flex items-center justify-center"
                    >
                        <span className="text-white">Chat</span>
                    </button>
                )}
            </div>
        </div>
    );
}
