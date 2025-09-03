import React from 'react';
import { X, ArrowRight, Split } from 'lucide-react';

interface ComparisonItem {
  title: string;
  snippet: string;
  link: string;
}

interface ComparisonBarProps {
  selectedItems: ComparisonItem[];
  onRemoveItem: (index: number) => void;
  onCompare: () => void;
}

const ComparisonBar: React.FC<ComparisonBarProps> = ({
  selectedItems,
  onRemoveItem,
  onCompare
}) => {
  if (selectedItems.length === 0) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white shadow-2xl border-t border-gray-200 p-4 z-50 transform transition-all duration-300">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-stretch space-x-4">
          {selectedItems.map((item, index) => (
            <div
              key={index}
              className="flex-1 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-4 relative min-h-[120px]"
            >
              <button
                onClick={() => onRemoveItem(index)}
                className="absolute top-2 right-2 p-1.5 rounded-full hover:bg-white/50 transition-colors"
                aria-label="Remove from comparison"
              >
                <X size={16} className="text-gray-600" />
              </button>
              <div className="pr-8">
                <h3 className="font-semibold text-gray-800 mb-2 line-clamp-1">
                  {item.title}
                </h3>
                <p className="text-sm text-gray-600 line-clamp-2">
                  {item.snippet}
                </p>
              </div>
            </div>
          ))}
          
          {selectedItems.length < 2 && (
            <div className="flex-1 border-2 border-dashed border-gray-300 rounded-xl flex flex-col items-center justify-center p-4 min-h-[120px] bg-gray-50">
              <Split className="w-6 h-6 text-gray-400 mb-2" />
              <p className="text-gray-500 text-center text-sm">
                Select another result to compare
              </p>
            </div>
          )}
          
          <div className="flex items-center pl-4">
            <button
              onClick={onCompare}
              disabled={selectedItems.length < 2}
              className={`px-6 py-3 rounded-xl font-medium flex items-center space-x-2 transition-all ${
                selectedItems.length === 2
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 shadow-lg'
                  : 'bg-gray-100 text-gray-400 cursor-not-allowed'
              }`}
            >
              <span>Compare</span>
              <ArrowRight size={16} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ComparisonBar;