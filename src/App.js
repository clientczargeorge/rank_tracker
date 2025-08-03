import './App.css';
import { useLocation } from 'react-router-dom';
import React, { useState, useEffect } from 'react';


function getRankSymbol(rank) {
    const symbol_map = {
        1: '➊',
        2: '➋',
        3: '➌',
        4: '➍',
        5: '➎',
        6: '➏',
        7: '➐',
        8: '➑',
        9: '➒',
        10: '➓',
    }

    if (symbol_map[rank]) {
        return (
            <span className="rank">{symbol_map[rank]}</span>
        );
    } else {
        return (
            <span className="rank">-</span>
        );
    }
}

function App() {
    const [rankList, setRankList] = useState([]);
    const clientName = "Avid Coffee";
    const clientUrl = "avidcoffee.com";
    const keywords = ['Petaluma Coffee', "bay area coffee", "coffee near petaluma CA", "avid coffee", "coffee in petaluma", "trendy coffee shopp petaluma", "best coffee petaluma", "coffee shop petaluma", "coffee roaster petaluma", "coffee roasters petaluma", "coffee shop near me", "coffee roaster near me", "coffee roasters near me", "best coffee near me", "best coffee in petaluma", "best coffee in bay area"];
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
                        // We assume the API returns an object like { google: 1 }, so we extract data[source]
                        keywordMap[phrase][source] = data[source];

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
            <h2>Rank Tracker</h2>
            <h3>Client: {clientName}</h3>
            <h3>Client URL: {clientUrl}</h3>
            <table>
                <thead>
                    <tr>
                        <th>Keyword Phrase</th>
                        <th>Google</th>
                        <th>Yahoo</th>
                        <th>Bing</th>
                        <th>Maps</th>
                    </tr>
                </thead>
                {rankList.map((row, index) => (
                    <tr key={index}>
                        <td>{row.keyword}</td>
                        <td>{getRankSymbol(row.google)}</td>
                        <td>{getRankSymbol(row.yahoo)}</td>
                        <td>{getRankSymbol(row.bing)}</td>
                        <td>{getRankSymbol(row.gmaps)}</td>
                    </tr>
                ))}
            </table>
        </>
    );
}


export default App;