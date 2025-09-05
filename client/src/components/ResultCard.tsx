import React, { useState, useEffect } from 'react';
import { ArrowRight, TrendingUp, ChevronUp, ChevronDown, Sparkles, Split } from 'lucide-react';

interface ResultCardProps {
  title: string;
  snippet: string;
  link: string;
  isSelectedForComparison: boolean;
  onSelectForComparison: () => void;
}

interface SummaryResponse {
  summary: string;
}

// Keep your existing helper functions
const getRandomLoadingText = () => {
  const loadingTexts = [
    " Crafting your personalized insights...",
    " Distilling wisdom from the content...",
    " Finding the perfect highlights for you ...",
    " Unveiling the essence of knowledge...",
    " Brewing your customized summary...",
    " Painting the big picture for you...",
    " Launching into the depths of content...",
    " Mining for valuable insights...",
    " Creating your rainbow of knowledge...",
    " Discovering hidden gems just for you...",
    " Powering up your understanding...",
    " Uncovering the story within...",
    " Setting the stage for clarity...",
    " Blossoming insights coming your way...",
    " Orchestrating your perfect summary..."
  ];
  return loadingTexts[Math.floor(Math.random() * loadingTexts.length)];
};

const getRandomSummaryTitle = () => {
  const titles = [
    " Key Insights Unveiled",
    " Your Curated Summary",
    " Essential Takeaways",
    " Knowledge Crystalized",
    " Summary Highlights",
    " Smart Brief"
  ];
  return titles[Math.floor(Math.random() * titles.length)];
};

const ResultCard: React.FC<ResultCardProps> = ({
  title,
  snippet,
  link,
  isSelectedForComparison,
  onSelectForComparison
}) => {
  const [summary, setSummary] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [loadingText, setLoadingText] = useState('');
  const [summaryTitle, setSummaryTitle] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [showSummary, setShowSummary] = useState(true);
  const [isSummaryGenerated, setIsSummaryGenerated] = useState(false);
  // const [isSelectedForComparison, setIsSelectedForComparison] = useState(false);

  useEffect(() => {
    if (isLoading) {
      const interval = setInterval(() => {
        setLoadingText(getRandomLoadingText());
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [isLoading]);

  const generateSummary = async () => {
    setIsLoading(true);
    setLoadingText(getRandomLoadingText());
    setError(null);

    try {
      const response = await fetch('https://sixthsense-xryg.onrender.com/summary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: link })
      });

      if (!response.ok) {
        throw new Error('Failed to generate summary');
      }

      const data: SummaryResponse = await response.json();
      setSummary(data.summary);
      setSummaryTitle(getRandomSummaryTitle());
      setIsSummaryGenerated(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleSummary = () => {
    setShowSummary(!showSummary);
  };



  return (
    <div className={`bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden ${isSelectedForComparison ? 'ring-2 ring-blue-500' : ''
      }`}>
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-800">{title}</h2>
          <button
            onClick={onSelectForComparison}
            className={`ml-4 p-2 rounded-lg transition-colors ${isSelectedForComparison
              ? 'bg-blue-100 text-blue-600'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            title="Compare"
          >
            <Split size={20} />
          </button>
        </div>

        <p className="text-gray-600 leading-relaxed mb-6">{snippet}</p>

        {isLoading && (
          <div className="mb-6">
            <div className="flex items-center justify-center space-x-3 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-4">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 font-medium text-lg transition-all duration-300">
                {loadingText}
              </span>
            </div>
          </div>
        )}

        {isSummaryGenerated && (
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <Sparkles className="w-5 h-5 text-purple-500" />
                <h3 className="text-lg font-semibold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
                  {summaryTitle}
                </h3>
              </div>
              <button
                onClick={toggleSummary}
                className="p-2 rounded-full hover:bg-gray-100 transition-colors"
                aria-label={showSummary ? 'Hide summary' : 'Show summary'}
              >
                {showSummary ? (
                  <ChevronUp className="w-5 h-5 text-gray-600" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-gray-600" />
                )}
              </button>
            </div>
            {showSummary && (
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-4 animate-fadeIn">
                <p className="text-gray-700 leading-relaxed">{summary}</p>
              </div>
            )}
          </div>
        )}

        {error && (
          <div className="text-red-500 mb-4">
            {error}
          </div>
        )}

        <div className="flex items-center justify-between pt-4 border-t">
          {!isSummaryGenerated && !isLoading && (
            <button
              onClick={generateSummary}
              className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 font-medium transition-colors"
            >
              <TrendingUp size={18} />
              <span>Generate Summary</span>
            </button>
          )}
          {(isSummaryGenerated || isLoading) && <div className="w-8" />}

          <a
            href={link}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-1 px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors"
          >
            <span>Learn more</span>
            <ArrowRight size={16} />
          </a>
        </div>
      </div>
    </div>
  );
};

export default ResultCard;