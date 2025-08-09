import './App.css';
import { useLocation } from 'react-router-dom';
import React, { useState, useEffect } from 'react';


function getRankSymbol(rank) {
    const symbol_map = {
        1:  (<span className="rank rank-1">➊</span>),
        2: (<span className="rank rank-2">➋</span>),
        3: (<span className="rank rank-3">➌</span>),
        4: (<span className="rank rank-4">➍</span>),
        5: (<span className="rank rank-5">➎</span>),
        6: (<span className="rank rank-6">➏</span>),
        7: (<span className="rank rank-7">➐</span>),
        8: (<span className="rank rank-8">➑</span>),
        9: (<span className="rank rank-9">➒</span>),
        10: (<span className="rank rank-10">➓</span>),
    }

    if (symbol_map[rank]) {
        return (symbol_map[rank]);
    } else {
        return (
            <span className="rank no-rank">⊘</span>
        );
    }
}

function App() {
    const [rankList, setRankList] = useState([]);

    const location = useLocation();
    const params = new URLSearchParams(location.search);

    const clientName = params.get('clientName') || '';
    const clientUrl = params.get('clientUrl') || '';

    const keywordsRaw = params.get('keywords') || '';
    const keywords = keywordsRaw.split(',').map(k => k.trim()).filter(k => k.length > 0);

    useEffect(() => {
        // A temporary in-memory object to store partially completed rows per keyword.
        // It accumulates results from multiple fetches (one per search engine).
        const keywordMap = {};

        // Loop through each keyword phrase that we want to track
        keywords.forEach((phrase) => {
            // Define which sources we want to fetch results from
            const sources = ['google', 'yahoo', 'bing', 'gmaps'];

            // For each source (e.g. Google, Yahoo), send a separate fetch request
            sources.forEach((source) => {
                // Construct the API URL dynamically with the correct query parameters
                const url = `http://localhost:5000/api?source=${source}&debug=false&client_url=${encodeURIComponent(clientUrl)}&client_name=${encodeURIComponent(clientName)}&keyword=${encodeURIComponent(phrase)}`;

                // Fetch results from the backend API
                fetch(url)
                    .then(res => res.json()) // Parse the response JSON
                    .then(data => {
                        // Initialize the keyword entry in keywordMap if it doesn't exist yet
                        keywordMap[phrase] = keywordMap[phrase] || { keyword: phrase };

                        // Save the result under the appropriate source name (e.g. "google", "bing", etc.)
                        // We assume the API returns an object like { google: 1, reference_url: "https://googl....." } so we extract both fields
                        // as a tuple that's stored in the keywordMap list.
                        keywordMap[phrase][source] = [data[source], data["reference_url"]];

                        // Update the React component's rank list state.
                        // This rebuilds the rank list with the updated row for this keyword.
                        setRankList(prevList => {
                            // Filter out any existing row for the same keyword (to avoid duplicates)
                            const otherRows = prevList.filter(row => row.keyword !== phrase);

                            // Add the updated row (from keywordMap) back into the list
                            // This allows the table to progressively show new data as each source arrives
                            return [...otherRows, keywordMap[phrase]];
                        });
                    })
                    .catch(err => {
                        // If something went wrong with this particular fetch, log it
                        console.error(`Fetch error for ${source} - ${phrase}:`, err);
                    });
            });
        });
    }, []); // Empty dependency array: this effect only runs once after the component mounts
    return (
        <>
            <h1>Rank Tracker</h1>
            <h2>Client Name: <code>{clientName}</code></h2>
            <h2>Client Website: <code>{clientUrl}</code></h2>
            <table>
                <thead>
                    <tr>
                        <th className="keyword">Keyword Phrase</th>
                        <th>Google</th>
                        <th>Yahoo</th>
                        <th>Bing</th>
                        <th>Maps</th>
                    </tr>
                </thead>
                <tbody>
                    {rankList.slice().sort((a, b) => a.keyword.localeCompare(b.keyword)).map((row, index) => (
                        <tr key={index}>
                            <td className="keyword">{row.keyword}</td>
                            <td>{row.google ? getRankSymbol(row.google[0]) : (<div className="spinner-container"><div className="spinner"></div></div>)} {row.google && (<a href={row.google[1]} target="_blank" rel="noopener noreferrer">View Google</a>)}</td>
                            <td>{row.yahoo ? getRankSymbol(row.yahoo[0]) : (<div className="spinner-container"><div className="spinner"></div></div>)} {row.yahoo && (<a href={row.yahoo[1]} target="_blank" rel="noopener noreferrer">View Yahoo</a>)}</td>
                            <td>{row.bing ? getRankSymbol(row.bing[0]) : (<div className="spinner-container"><div className="spinner"></div></div>)} {row.bing && (<a href={row.bing[1]} target="_blank" rel="noopener noreferrer">View Bing</a>)}</td>
                            <td>{row.gmaps ? getRankSymbol(row.gmaps[0]) : (<div className="spinner-container"><div className="spinner"></div></div>)} {row.gmaps && (<a href={row.gmaps[1]} target="_blank" rel="noopener noreferrer">View Maps</a>)}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </>
    );
}


export default App;