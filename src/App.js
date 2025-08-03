import './App.css';
import { useLocation } from 'react-router-dom';
import React, { useState, useEffect } from 'react';

function App() {
    const [rankList, setRankList] = useState([]);
    const clientName = "Avid Coffee";
    const clientUrl = "avidcoffee.com";
    const keywords = ['Petaluma Coffee', "bay area coffee", "coffee near petaluma CA", "avid coffee"];
    useEffect(() => {

        keywords.forEach(phrase => {
            const url = `http://localhost:5000/api?debug=true&client_url=${encodeURIComponent(clientUrl)}&client_name=${encodeURIComponent(clientName)}&keyword=${encodeURIComponent(phrase)}`;

            Promise.all([
                fetch(url).then(res => res.json()), // bing
                fetch(url).then(res => res.json()), // google
                fetch(url).then(res => res.json()), // maps
                fetch(url).then(res => res.json()), // yahoo
            ]).then(([bing, google, maps, yahoo]) => {
                const newRow = {
                    keyword: phrase,
                    bing: bing.bing,
                    google: google.google,
                    maps: maps.maps,
                    yahoo: yahoo.yahoo,
                };

                setRankList(prevList => [...prevList, newRow]);
            }).catch(err => {
                console.error(`Error fetching results for ${phrase}:`, err);
            });
        });
    }, []);

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
                        <td>{row.google}</td>
                        <td>{row.yahoo}</td>
                        <td>{row.bing}</td>
                        <td>{row.maps}</td>
                    </tr>
                ))}
            </table>
        </>
    );
}


export default App;