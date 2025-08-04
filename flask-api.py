from flask import Flask, jsonify, request
from flask_cors import CORS
import serpapi
from urllib.parse import urlencode, quote_plus
import random

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

    debug = (request.args.get("debug") == "true")

    if source == "google":
        # Get Google ranking for the client URL
        params = {
            "q": keyword,
            "engine": "google",
            "google_domain": "google.com",
            "hl": "en",
            "gl": "us"
        }

        reference_url = f"https://www.google.com/search?{urlencode(params)}"

        if debug:
            return jsonify({
                "google": random.randint(0, 10),
                "reference_url": reference_url,
            })

        s = serp_client.search(**params)
        organic_results_list = s["organic_results"]
        for entry in organic_results_list:
            if client_url == urlparse(entry.get("link")).netloc:
                client_ranking_google = entry.get("position")
                return jsonify({
                    "google": client_ranking_google,
                    "reference_url": reference_url,
                })
        # If no ranking found, return -1
        return jsonify({
            "google": -1,
            "reference_url": reference_url
        })

    elif source == "bing":

        params = {
            "q": keyword,
            "engine": "bing",
            "hl": "en",
            "gl": "us"
        }

        reference_url = f"https://www.bing.com/search?{urlencode(params)}"

        if debug:
            return jsonify({
                "bing": random.randint(0, 10),
                "reference_url": reference_url,
            })

        # Get Bing ranking for the client URL
        s = serp_client.search(**params)
        organic_results_list = s["organic_results"]
        for entry in organic_results_list:
            if client_url == urlparse(entry.get("link")).netloc:
                client_ranking_bing = entry.get("position")
                return jsonify({
                    "bing": client_ranking_bing,
                    "reference_url": reference_url,
                })
        # If no ranking found, return -1
        return jsonify({
            "bing": -1,
            "reference_url": reference_url,
        })

    elif source == "yahoo":

        params = {
            "p": keyword,
            "engine": "yahoo",
            "hl": "en",
            "gl": "us"
        }

        reference_url = f"https://search.yahoo.com/search?{urlencode(params)}"

        if debug:
            return jsonify({
                "yahoo": random.randint(0, 10),
                "reference_url": reference_url,
            })

        # Get Yahoo ranking for the client URL
        s = serp_client.search(**params)
        organic_results_list = s["organic_results"]
        for entry in organic_results_list:
            if client_url == urlparse(entry.get("link")).netloc:
                client_ranking_yahoo = entry.get("position")
                return jsonify({
                    "yahoo": client_ranking_yahoo,
                    "reference_url": reference_url,
                })
        # If no ranking found, return -1
        return jsonify({
            "yahoo": -1,
            "reference_url": reference_url,
        })

    elif source == "gmaps":

        params = {
            "q": keyword,
            "engine": "google_maps",
            "hl": "en",
            "gl": "us"
        }

        reference_url = f"https://www.google.com/maps/search/{quote_plus(params['q'])}?{urlencode({'hl': params['hl'], 'gl': params['gl']})}"

        if debug:
            return jsonify({
                "gmaps": random.randint(0, 10),
                "reference_url": reference_url,
            })

        # Get Google Maps ranking for the client URL
        s = serp_client.search(**params)
        results_list = s["local_results"]
        for entry in results_list:
            if client_name == entry.get("title"):
                client_ranking_gmaps = entry.get("position")
                return jsonify({
                    "gmaps": client_ranking_gmaps,
                    "reference_url": reference_url,
                })
        # If no ranking found, return -1
        return jsonify({
            "gmaps": -1,
            "reference_url": reference_url,
        })

    return "error"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)