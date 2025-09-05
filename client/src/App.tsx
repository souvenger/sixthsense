import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation, useNavigate } from 'react-router-dom';
import ResultCard from './components/ResultCard';
import ComparisonBar from './components/ComparisonBar';
import ComparisonHeader from './components/ComparisonHeader';
import SearchHomepage from './components/SearchHomepage';
import WebsiteComparison from './components/comparatorPage';



const getLanguageTitle = (title: string): string => {
  return `${title}`;
};

const useQuery = () => {
  return new URLSearchParams(useLocation().search);
};

interface SearchResults {
  results: Array<{
    link: string;
    rank: number;
    snippet: string;
    title: string;
  }>;
}

interface SummaryResponse {
  summary_result: string[];
}

const RESULTS_PER_PAGE = 10;

const ResultsPage = () => {
  const query = useQuery().get('query') || '';
  const pageParam = useQuery().get('page');
  const currentPage = pageParam ? parseInt(pageParam) : 1;

  const [searchQuery, setSearchQuery] = useState(query);
  const [sentences, setSentences] = useState<SummaryResponse>({ summary_result: [] });
  const [results, setResults] = useState<SearchResults>({ results: [] });
  const [loading, setLoading] = useState(false);
  const [sentencesLoading, setSentencesLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedItems, setSelectedItems] = useState<Array<{
    title: string;
    snippet: string;
    link: string;
  }>>([]);
  const navigate = useNavigate();

  const totalPages = Math.ceil((results.results?.length || 0) / RESULTS_PER_PAGE);
  const startIndex = (currentPage - 1) * RESULTS_PER_PAGE;
  const endIndex = startIndex + RESULTS_PER_PAGE;
  const currentResults = results.results?.slice(startIndex, endIndex) || [];

  useEffect(() => {
    if (query) {
      fetchResults();
    }
  }, []);

  const fetchResults = async () => {
    setLoading(true);
    setError(null);

    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 15000);
      const response = await fetch('https://sixthsense-xryg.onrender.com/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: searchQuery }),
        signal: controller.signal,
      });
      clearTimeout(timeout);

      if (!response.ok) {
        throw new Error('Failed to fetch search results');
      }

      const data = await response.json();
      const sortedResults = (data.results || []).sort((a: any, b: any) => a.rank - b.rank);
      setResults({ results: sortedResults });
      setSentences({ summary_result: Array.isArray(data.summary_result) ? data.summary_result : [] });
    } catch (error) {
      setError('There was an error fetching the results.');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // Summary now comes with /search response
  const fetchSentences = async (_isInitial: boolean = false) => { };

  const handleSelectForComparison = (result: { title: string; snippet: string; link: string }) => {
    setSelectedItems(prev => {
      // If item is already selected, remove it
      if (prev.some(item => item.link === result.link)) {
        return prev.filter(item => item.link !== result.link);
      }
      // If we already have 2 items, don't add more
      if (prev.length >= 2) {
        return prev;
      }
      // Add the new item
      return [...prev, result];
    });
  };

  const handleRemoveFromComparison = (index: number) => {
    setSelectedItems(prev => prev.filter((_, i) => i !== index));
  };

  const handleCompare = async () => {
    if (selectedItems.length < 2) {
      alert("Please select two items for comparison.");
      return;
    }

    const url1 = selectedItems[0].link;
    const url2 = selectedItems[1].link;
    const title1 = selectedItems[0].title;
    const title2 = selectedItems[1].title;

    window.open(`/compare-results?url1=${encodeURIComponent(url1)}&url2=${encodeURIComponent(url2)}&title1=${encodeURIComponent(title1)}&title2=${encodeURIComponent(title2)}`, "_blank");
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  const handleSearchSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    navigate(`/search?query=${searchQuery}&page=1`);
    fetchResults();
  };


  const handlePageChange = (page: number) => {
    navigate(`/search?query=${searchQuery}&page=${page}`);
  };

  const PaginationControls = () => (
    <div className="flex justify-center items-center space-x-2 mt-8">
      <button
        onClick={() => handlePageChange(currentPage - 1)}
        disabled={currentPage === 1}
        className={`px-4 py-2 rounded ${currentPage === 1
          ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
          : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
      >
        Previous
      </button>
      <div className="flex space-x-1">
        {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
          <button
            key={page}
            onClick={() => handlePageChange(page)}
            className={`px-4 py-2 rounded ${currentPage === page
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
          >
            {page}
          </button>
        ))}
      </div>
      <button
        onClick={() => handlePageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        className={`px-4 py-2 rounded ${currentPage === totalPages
          ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
          : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
      >
        Next
      </button>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 pb-32">
      <ComparisonHeader
        searchQuery={searchQuery}
        onSearchChange={handleSearchChange}
        onSearchSubmit={handleSearchSubmit}
      />

      <main className="container mx-auto px-4 py-12">
        <div className="max-w-5xl mx-auto">
          {currentPage === 1 && (
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-8 mb-12 shadow-sm">
              <h2 className="text-2xl font-bold text-gray-800 mb-6">Search Results</h2>
              {loading && <div>Loading...</div>}
              {error && <div className="text-red-500">{error}</div>}
              {!loading && !error && sentences.summary_result && sentences.summary_result.length > 0 && (
                <div className="space-y-4">
                  {sentences.summary_result.map((sentence, index) => (
                    <div key={index} className="flex items-center space-x-3">
                      <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                        {index + 1}
                      </div>
                      <div className="text-gray-700 flex-1">{sentence}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          <div className="grid gap-8">
            {currentResults.map((result, index) => (
              <ResultCard
                key={index}
                title={getLanguageTitle(result.title)}
                snippet={result.snippet}
                link={result.link}
                isSelectedForComparison={selectedItems.some(item => item.link === result.link)}
                onSelectForComparison={() => handleSelectForComparison({
                  title: result.title,
                  snippet: result.snippet,
                  link: result.link
                })}
              />
            ))}
          </div>

          {results.results && results.results.length > 0 && <PaginationControls />}

          {!loading && !error && (!results.results || results.results.length === 0) && (
            <div className="text-center text-gray-600">No results found.</div>
          )}
        </div>
      </main>
      <ComparisonBar
        selectedItems={selectedItems}
        onRemoveItem={handleRemoveFromComparison}
        onCompare={handleCompare}
      />
    </div>
  );
};

function App() {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    window.location.href = `/search?query=${searchQuery}&page=1`;
  };

  return (
    <Router>
      <Routes>
        <Route
          path="/"
          element={
            <SearchHomepage
              searchQuery={searchQuery}
              onSearchChange={handleSearchChange}
              onSearchSubmit={handleSearchSubmit}
            />
          }
        />
        <Route path="/search" element={<ResultsPage />} />
        <Route path="/compare-results" element={<WebsiteComparison />} />
      </Routes>
    </Router>
  );
}

export default App;