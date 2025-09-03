import { SearchResult } from '../types';

export const searchResults = (results: SearchResult[], query: string): SearchResult[] => {
  const searchTerm = query.toLowerCase().trim();
  if (!searchTerm) return results;

  return results.filter(result =>
    result.title.toLowerCase().includes(searchTerm) ||
    result.snippet.toLowerCase().includes(searchTerm) ||
    result.link.toLowerCase().includes(searchTerm)
  );
};
