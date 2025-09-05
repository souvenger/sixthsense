import React from 'react';
import { Search, Eye } from 'lucide-react';
// import { Search, Eye } from "lucide-react";

interface ComparisonHeaderProps {
  searchQuery: string;
  onSearchChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onSearchSubmit: (e: React.FormEvent) => void;
}

const ComparisonHeader: React.FC<ComparisonHeaderProps> = ({
  searchQuery,
  onSearchChange,
  onSearchSubmit
}) => {
  return (

    <header className="bg-gradient-to-r from-blue-600 to-blue-800 text-white">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2">
              <img src="/logo.png" alt="Sixth Sense" className="w-12 h-12" />
            </div>

            <h1 className="text-2xl font-bold tracking-tight">SixthSense</h1>

            {/* SEARCH FORM */}
            <form onSubmit={onSearchSubmit} className="ml-14 w-[500px]">
              <div className="relative flex items-center">
                {/* Search Icon */}
                <Search
                  className="absolute right-4 text-gray-400 group-hover:text-blue-500 transition-colors"
                  size={20}
                />

                {/* Search Input */}
                <input
                  type="text"
                  placeholder="Search With Our Sixth Sense..."
                  value={searchQuery}
                  onChange={onSearchChange}
                  className="w-full pl-4 pr-24 py-3 rounded-xl border border-white/30 bg-white/10 text-white placeholder:text-white/70 focus:outline-none focus:border-white/50 transition-all mx-auto"
                />

                {/* Simple Animated Eye */}
                {/* <div className="eye-container">
                  <div className="iris">
                    <div className="pupil"></div>
                  </div>
                  <div className="eyelid"></div>
                </div> */}

              </div>
            </form>
          </div>
          <div className="flex-shrink-0"></div> {/* Space on the right */}
        </div>
      </div>
    </header>

  );
};

export default ComparisonHeader;