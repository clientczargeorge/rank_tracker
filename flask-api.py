from flask import Flask, jsonify, request
from flask_cors import CORS
import serpapi

# importing os module for environment variables
import os
# importing necessary functions from dotenv library
from dotenv import load_dotenv, dotenv_values

from urllib.parse import urlparse

app = Flask(__name__)

# loading variables from .env file
load_dotenv()

CORS(app)

serp_client = serpapi.Client(api_key=os.getenv("SERP_KEY"))

@app.route('/api')
def serp_results():
    client_url = request.args.get("client_url")
    client_name = request.args.get("client_name")
    keyword = request.args.get("keyword")
    source = request.args.get("source")

    if request.args.get("debug") == "true":
        return jsonify({
            "gmaps": 0,
            "google":1,
            "yahoo": 2,
            "bing": 0
        })

    if source == "google":
        # Get Google ranking for the client URL
        s = serp_client.search(q=keyword, engine="google", google_domain="google.com", hl="en", gl="us")
        organic_results_list = s["organic_results"]
        for entry in organic_results_list:
            if client_url == urlparse(entry.get("link")).netloc:
                client_ranking_google = entry.get("position")
                return jsonify({
                    "google": client_ranking_google,
                })
        # If no ranking found, return -1
        return jsonify({
            "google": -1,
        })

    elif source == "bing":
        # Get Bing ranking for the client URL
        s = serp_client.search(q=keyword, engine="bing", hl="en", gl="us")
        organic_results_list = s["organic_results"]
        for entry in organic_results_list:
            if client_url == urlparse(entry.get("link")).netloc:
                client_ranking_bing = entry.get("position")
                return jsonify({
                    "bing": client_ranking_bing,
                })
        # If no ranking found, return -1
        return jsonify({
            "bing": -1,
        })

    elif source == "yahoo":
        # Get Yahoo ranking for the client URL
        s = serp_client.search(p=keyword, engine="yahoo", hl="en", gl="us")
        organic_results_list = s["organic_results"]
        for entry in organic_results_list:
            if client_url == urlparse(entry.get("link")).netloc:
                client_ranking_yahoo = entry.get("position")
                return jsonify({
                    "yahoo": client_ranking_yahoo,
                })
        # If no ranking found, return -1
        return jsonify({
            "yahoo": -1,
        })

    elif source == "gmaps":
        # Get Google Maps ranking for the client URL
        s = serp_client.search(q=keyword, engine="google_maps", hl="en", gl="us")
        results_list = s["local_results"]
        for entry in results_list:
            if client_name == entry.get("title"):
                client_ranking_gmaps = entry.get("position")
                return jsonify({
                    "gmaps": client_ranking_gmaps,
                })
        # If no ranking found, return -1
        return jsonify({
            "gmaps": -1,
        })

    return "error"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)