import React from "react";

function Footer() {
    return (
        <footer className="bg-gray-900 text-gray-400 text-center py-8 mt-8">
            <p>© {new Date().getFullYear()} RCPY. All Rights Reserved.</p>
            <p className="text-sm mt-2 pb-2">
                Created with ❤️ for culinary enthusiasts.
            </p>
        </footer>
    );
}

export default Footer;
