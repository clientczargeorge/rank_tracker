import './App.css';
import { useLocation } from 'react-router-dom';
import React, { useState, useEffect } from 'react';

// import images
import googleLogo from './images/google_logo.png';
import yahooLogo from './images/yahoo_logo.png';
import gmapsLogo from './images/gmaps_logo.png';
import bingLogo from './images/bing_logo.png';
import rankTrackerLogo from './images/Search_Rank_Tracker_Logo.png';


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

// cache.js
export function setCache(key, value, ttlSeconds) {
  const expiresAt = Date.now() + ttlSeconds * 1000;
  const item = { value, expiresAt };
  localStorage.setItem(key, JSON.stringify(item));
}

export function getCache(key) {
  const itemStr = localStorage.getItem(key);
  if (!itemStr) return null;

  try {
    const item = JSON.parse(itemStr);
    if (Date.now() > item.expiresAt) {
      localStorage.removeItem(key); // expired
      return null;
    }
    return item.value;
  } catch {
    return null;
  }
}

function App() {
    const [rankList, setRankList] = useState([]);

    const location = useLocation();
    const params = new URLSearchParams(location.search);

    const clientName = params.get('clientName') || '';
    const clientUrl = params.get('clientUrl') || '';
    const clientLocation = params.get('clientLocation') || '';
    const clientCoordinates = params.get('clientCoordinates') || '';
    const gmapsName = params.get('gmapsName') || '';
    const refresh = params.get('refresh') || '';
    const debug = params.get('debug') || '';

    const keywordsRaw = params.get('keywords') || '';
    const keywords = keywordsRaw.split(',').map(k => k.trim()).filter(k => k.length > 0);

    const hasParams = clientName && clientUrl && gmapsName && keywords.length > 0;

    // How long should values be stored in the user's browser?
    const ttlSeconds = 10800; // 3 hours

    useEffect(() => {
        if (!hasParams) return; // skip fetching if no params provided

        // A temporary in-memory object to store partially completed rows per keyword.
        // It accumulates results from multiple fetches (one per search engine).
        const keywordMap = {};

        // Define which sources we want to fetch results from
        const sources = ['google', 'yahoo', 'bing', 'gmaps'];

        // Loop through each keyword phrase that we want to track
        keywords.forEach((phrase) => {
            // For each source (e.g. Google, Yahoo), send a separate fetch request
            sources.forEach((source) => {
                // Construct the API URL dynamically with the correct query parameters
                const url = `http://localhost:5000/api?source=${source}&debug=${debug}&refresh=${refresh}&client_url=${encodeURIComponent(clientUrl)}&client_name=${encodeURIComponent(clientName)}&keyword=${encodeURIComponent(phrase)}&client_location=${encodeURIComponent(clientLocation)}&client_coordinates=${encodeURIComponent(clientCoordinates)}&gmaps_name=${encodeURIComponent(gmapsName)}`;
                //const url = `https://rank-tracker.duckdns.org/api?source=${source}&debug=${debug}&refresh=${refresh}&client_url=${encodeURIComponent(clientUrl)}&client_name=${encodeURIComponent(clientName)}&keyword=${encodeURIComponent(phrase)}&client_location=${encodeURIComponent(clientLocation)}&client_coordinates=${encodeURIComponent(clientCoordinates)}`;

                // Create a unique cache key
                const cacheKey = `${source}:${phrase}:${clientUrl}:${clientLocation}:${clientCoordinates}`;

                // Check cache first
                const cached = getCache(cacheKey);
                if (cached) {
                    keywordMap[phrase] = keywordMap[phrase] || { keyword: phrase };
                    keywordMap[phrase][source] = cached;

                    setRankList(prevList => {
                        const otherRows = prevList.filter(row => row.keyword !== phrase);
                        return [...otherRows, keywordMap[phrase]];
                    });

                    return; // Skip fetch if cached
                }

                fetch(url)
                    .then(res => res.json())
                    .then(data => {
                        const value = [data[source], data["reference_url"]];

                        // save into cache
                        setCache(cacheKey, value, ttlSeconds);

                        keywordMap[phrase] = keywordMap[phrase] || { keyword: phrase };
                        keywordMap[phrase][source] = value;

                        setRankList(prevList => {
                            const otherRows = prevList.filter(row => row.keyword !== phrase);
                            return [...otherRows, keywordMap[phrase]];
                        });
                    })
                    .catch(err => {
                        console.error(`Fetch error for ${source} - ${phrase}:`, err);
                    });
            });
        });
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []); // Empty dependency array: this effect only runs once after the component mounts. Otherwise you see weird jitters.

    if (!hasParams) {
        return (
            <div className="instructions">
                <h1>Rank Tracker</h1>
                <p>
                    No query parameters detected.
                    Please supply the following fields:
                    clientUrl: The client's website URL (e.g. avidcoffee.com)<br/>
                    clientName: The client's business name (e.g. Avid Coffee)<br/>
                    gmapsName: The name of the business as it appears in Google Maps (e.g. Avid Coffee)<br/>
                    keywords: A comma-separated list of keyword phrases to track (e.g. Petaluma coffee,avid+coffee,sonoma+county+coffee,coffee+roasterz)<br/>
                    Optionally, you can also supply:
                    clientLocation: The city or area to use for localized search (google & bing only) (e.g. petaluma)<br/>
                    clientCoordinates: The latitude and longitude to use for Google Maps localized search. MUST be in this format exactly: @38.244923,-122.626991,14z<br/>
                    Example:
                </p>
                <pre>
                    {`${window.location.origin}?clientName=Avid Coffee&clientUrl=avidcoffee.com&gmapsName=Avid Coffee&keywords=Petaluma coffee,avid+coffee,sonoma+county+coffee,coffee+roasterz&location=petaluma&coordinates,coordinates=@38.244923,-122.626991,14z&refresh=false`}
                </pre>
            </div>
        );
    }

    return (
        <>
            <h1>
                <img src={rankTrackerLogo} alt="Rank Tracker Logo" className="h1-logo logo"/>
            </h1>
            <h2>Client Name: <code>{clientName}</code></h2>
            <h2>Client Website: <code>{clientUrl}</code></h2>
            <table>
                <thead>
                <tr>
                    <th className="keyword"><h3>Keyword Phrase</h3></th>
                    <th><h3>Maps</h3><h4>Local Search</h4><img src={gmapsLogo} alt="Google Maps Logo"
                                                               className="column-logo"/></th>
                    <th><h3>Google</h3><h4>Organic Search</h4><img src={googleLogo} alt="Google Search Logo"
                                                                   className="column-logo"/></th>
                    <th><h3>Yahoo</h3><h4>Organic Search</h4><img src={yahooLogo} alt="Yahoo Logo"
                                                                  className="column-logo"/></th>
                    <th><h3>Bing</h3><h4>Organic Search</h4><img src={bingLogo} alt="Bing Logo"
                                                                 className="column-logo"/></th>
                </tr>
                </thead>
                <tbody>
                {keywords.slice().sort().map((phrase) => {
                    const row = rankList.find(r => r.keyword === phrase) || {keyword: phrase};

                    return (
                        <tr key={phrase}>
                            <td className="keyword">{row.keyword}</td>

                            <td>
                                {row.gmaps
                                    ? getRankSymbol(row.gmaps[0])
                                    : <div className="spinner-container">
                                        <div className="spinner"></div>
                                    </div>}
                                {row.gmaps && (
                                    <a href={row.gmaps[1]} target="_blank" rel="noopener noreferrer">View Maps</a>
                                )}
                            </td>

                            <td>
                                {row.google
                                    ? getRankSymbol(row.google[0])
                                    : <div className="spinner-container">
                                        <div className="spinner"></div>
                                    </div>}
                                {row.google && (
                                    <a href={row.google[1]} target="_blank" rel="noopener noreferrer">View Google</a>
                                )}
                            </td>

                            <td>
                                {row.yahoo
                                    ? getRankSymbol(row.yahoo[0])
                                    : <div className="spinner-container">
                                        <div className="spinner"></div>
                                    </div>}
                                {row.yahoo && (
                                    <a href={row.yahoo[1]} target="_blank" rel="noopener noreferrer">View Yahoo</a>
                                )}
                            </td>

                            <td>
                                {row.bing
                                    ? getRankSymbol(row.bing[0])
                                    : <div className="spinner-container">
                                        <div className="spinner"></div>
                                    </div>}
                                {row.bing && (
                                    <a href={row.bing[1]} target="_blank" rel="noopener noreferrer">View Bing</a>
                                )}
                            </td>
                        </tr>
                    );
                })}
                </tbody>
            </table>
        </>
    );
}


export default App;
