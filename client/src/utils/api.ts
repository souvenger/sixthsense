const BASE_URL = 'http://localhost:5000/api';

export const fetchWithRetry = async (url: string, retries = 3, delay = 1000) => {
  for (let i = 0; i < retries; i++) {
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      if (i === retries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
};

export const api = {
  getLanguages: () => fetchWithRetry(`${BASE_URL}/languages`),
  searchResults: (query: string) => fetchWithRetry(`${BASE_URL}/search?q=${encodeURIComponent(query)}`),
};