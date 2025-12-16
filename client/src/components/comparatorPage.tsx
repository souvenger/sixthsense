import { BASE_URL } from "../config";
import React, { useState, useEffect } from "react";
import { ExternalLink, ArrowRightLeft } from "lucide-react";

interface Website {
    url: string;
    title: string;
    keyPoints: string[];
    uniqueFeatures: string[];
    contentStructure: {
        introduction: string;
        mainContent: string;
        conclusion: string;
    };
    advantages: string[];
    limitations: string[];
}

const WebsiteComparison = () => {
    const [websites, setWebsites] = useState<Website[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Get URL parameters without react-router-dom
    const urlParams = new URLSearchParams(window.location.search);
    const url1 = urlParams.get("url1");
    const url2 = urlParams.get("url2");
    const title1 = urlParams.get("title1");
    const title2 = urlParams.get("title2");

    useEffect(() => {
        if (!url1 || !url2) {
            setLoading(false);
            return;
        }

        const fetchData = async () => {
            try {
                const controller = new AbortController();
                const timeout = setTimeout(() => controller.abort(), 20000);
                const response = await fetch(`${BASE_URL}/compare`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ url1, url2, title1, title2 }),
                    signal: controller.signal,
                });
                clearTimeout(timeout);
                if (!response.ok) throw new Error("API call failed");
                const data = await response.json();
                setWebsites(data.websites);
                setError(null);
            } catch (error: any) {
                console.error("Error fetching website data:", error);
                setError(error?.message || 'Failed to load comparison');
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [url1, url2]);

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="animate-pulse text-lg text-gray-600">
                    Loading website comparison...
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-lg text-red-600 bg-red-50 p-6 rounded-lg shadow">
                    {error}
                </div>
            </div>
        );
    }

    if (!websites || websites.length < 2) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-lg text-red-600 bg-red-50 p-6 rounded-lg shadow">
                    Not enough data to compare websites.
                </div>
            </div>
        );
    }

    const ContentSection = ({ title, children }) => (
        <div className="mb-8 bg-white rounded-lg p-6 shadow-sm">
            <h3 className="font-semibold text-xl mb-4 text-blue-700 border-b pb-2">{title}</h3>
            {children}
        </div>
    );

    const ComparisonRow = ({ site1, site2 }) => (
        <div className="grid grid-cols-2 gap-6 mb-4">
            <div className="p-4 bg-gray-50 rounded-lg shadow-inner">
                <ul className="list-disc pl-5 space-y-3 text-gray-700">
                    {Array.isArray(site1) ? site1.map((item, index) => (
                        <li key={index} className="leading-relaxed">{item}</li>
                    )) : <li className="leading-relaxed">{site1}</li>}
                </ul>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg shadow-inner">
                <ul className="list-disc pl-5 space-y-3 text-gray-700">
                    {Array.isArray(site2) ? site2.map((item, index) => (
                        <li key={index} className="leading-relaxed">{item}</li>
                    )) : <li className="leading-relaxed">{site2}</li>}
                </ul>
            </div>
        </div>
    );

    return (
        <div className="max-w-6xl mx-auto py-8 px-4">
            <div className="bg-white rounded-xl shadow-lg overflow-hidden">
                <div className="bg-gradient-to-r from-blue-500 to-blue-600 p-8">
                    <h2 className="text-3xl font-bold text-center flex items-center justify-center gap-6 text-white">
                        <a href={websites[0].url} target="_blank" rel="noopener noreferrer"
                            className="hover:text-blue-100 transition-colors flex items-center gap-2">
                            {websites[0].title}
                            <ExternalLink className="w-5 h-5" />
                        </a>
                        <ArrowRightLeft className="w-8 h-8 text-blue-200" />
                        <a href={websites[1].url} target="_blank" rel="noopener noreferrer"
                            className="hover:text-blue-100 transition-colors flex items-center gap-2">
                            {websites[1].title}
                            <ExternalLink className="w-5 h-5" />
                        </a>
                    </h2>
                </div>

                <div className="p-8 space-y-8 bg-gray-50">
                    <ContentSection title="Key Information">
                        <ComparisonRow site1={websites[0].keyPoints} site2={websites[1].keyPoints} />
                    </ContentSection>

                    <ContentSection title="Content Structure">
                        <ComparisonRow
                            site1={websites[0].contentStructure.mainContent}
                            site2={websites[1].contentStructure.mainContent}
                        />
                    </ContentSection>

                    <ContentSection title="Unique Features">
                        <ComparisonRow site1={websites[0].uniqueFeatures} site2={websites[1].uniqueFeatures} />
                    </ContentSection>

                    <ContentSection title="Strengths & Limitations">
                        <div className="space-y-6">
                            <div>
                                <div className="grid grid-cols-2 gap-6 mb-3">
                                    <h4 className="text-green-600 font-semibold text-lg">Advantages</h4>
                                    <h4 className="text-green-600 font-semibold text-lg">Advantages</h4>
                                </div>
                                <ComparisonRow site1={websites[0].advantages} site2={websites[1].advantages} />
                            </div>
                            <div>
                                <div className="grid grid-cols-2 gap-6 mb-3">
                                    <h4 className="text-red-600 font-semibold text-lg">Limitations</h4>
                                    <h4 className="text-red-600 font-semibold text-lg">Limitations</h4>
                                </div>
                                <ComparisonRow site1={websites[0].limitations} site2={websites[1].limitations} />
                            </div>
                        </div>
                    </ContentSection>

                    <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-xl p-6 shadow-inner">
                        <h3 className="text-xl font-semibold mb-4 text-blue-800">Content Analysis Summary</h3>
                        <div className="space-y-4 text-gray-700">
                            <p className="flex items-center gap-2">
                                <span className="font-semibold text-blue-700">Best for Beginners:</span>
                                {websites[1].title} offers a simpler introduction.
                            </p>
                            <p className="flex items-center gap-2">
                                <span className="font-semibold text-blue-700">Best for Comprehensive Learning:</span>
                                {websites[0].title} provides detailed explanations.
                            </p>
                            <p className="flex items-center gap-2">
                                <span className="font-semibold text-blue-700">Recommendation:</span>
                                Choose based on learning preference.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default WebsiteComparison;