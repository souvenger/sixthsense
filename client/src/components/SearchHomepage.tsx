import React, { useState } from 'react';
import { Search, Mic, Camera } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const SearchHomepage = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const [isFocused, setIsFocused] = useState(false);
    const navigate = useNavigate(); // For navigation

    const handleSearch = (e) => {
        e.preventDefault();
        if (searchQuery.trim() === '') return; // Prevent empty search
        navigate(`/search?query=${encodeURIComponent(searchQuery)}`); // Redirect with query
    };

    return (
        <div className="h-screen bg-gradient-to-b from-pink-50 via-blue-50 to-purple-50 flex flex-col">
            {/* Main Content Container */}
            <div className="flex-1 flex flex-col items-center justify-center pb-32">
                {/* Logo Section */}
                <div className="mb-8">
                    <h1 className="text-6xl font-bold bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 bg-clip-text text-transparent animate-pulse">
                        Sixth Sense
                    </h1>
                </div>

                {/* Search Section */}
                <div className="w-full max-w-2xl px-4">
                    <form onSubmit={handleSearch}>
                        <div className={`relative flex items-center rounded-full border backdrop-blur-sm bg-white/70 ${isFocused
                            ? 'border-purple-400 shadow-lg shadow-purple-200' : 'border-gray-200 shadow-sm'} hover:shadow-md
            hover:shadow-purple-100 transition-all duration-300`}>
                            {/* Search Icon */}
                            <div className="pl-4 text-purple-500">
                                <Search size={20} />
                            </div>

                            {/* Search Input */}
                            <input
                                type="text"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                onFocus={() => setIsFocused(true)}
                                onBlur={() => setIsFocused(false)}
                                className="w-full py-4 px-4 outline-none rounded-full text-gray-700 bg-transparent placeholder-purple-300"
                                placeholder="Search with Our Sixth Sense..."
                            />
                        </div>

                        {/* Search Buttons */}
                        <div className="flex justify-center gap-4 mt-8">
                            <button
                                type="button"
                                onClick={() => {
                                    setSearchQuery("What are LLMs?");
                                    setTimeout(() => handleSearch(), 100); // Delay to update state
                                }}
                                className="px-8 py-3 bg-gradient-to-r from-purple-400 to-pink-400 hover:from-purple-500 hover:to-pink-500 text-white text-sm rounded-full shadow-md hover:shadow-lg transition-all duration-300">
                                What are LLMs?
                            </button>

                            <button
                                type="button"
                                onClick={() => {
                                    setSearchQuery("Best free open-source AI code editors");
                                    setTimeout(() => handleSearch(), 100);
                                }}
                                className="px-8 py-3 bg-gradient-to-r from-indigo-400 to-blue-400 hover:from-indigo-500 hover:to-blue-500 text-white text-sm rounded-full shadow-md hover:shadow-lg transition-all duration-300">
                                Best free open-source AI code editors
                            </button>
                        </div>
                    </form>
                </div>
            </div>

            {/* Footer can be removed without affecting layout */}
            {/* <footer className="w-full bg-white/50 backdrop-blur-sm text-sm text-gray-600">
                <div className="border-b border-purple-100 py-3 px-8">
                    <span>United States</span>
                </div>
                <div className="flex justify-between py-3 px-8">
                    <div className="flex gap-6">
                        <a href="#" className="hover:text-purple-500 transition-colors">About</a>
                        <a href="#" className="hover:text-purple-500 transition-colors">Advertising</a>
                        <a href="#" className="hover:text-purple-500 transition-colors">Business</a>
                    </div>
                    <div className="flex gap-6">
                        <a href="#" className="hover:text-purple-500 transition-colors">Privacy</a>
                        <a href="#" className="hover:text-purple-500 transition-colors">Terms</a>
                        <a href="#" className="hover:text-purple-500 transition-colors">Settings</a>
                    </div>
                </div>
            </footer> */}
        </div>
    );
};

export default SearchHomepage;