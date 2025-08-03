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

    if request.args.get("debug") == "true":
        return jsonify({
            "keyword": -1,
            "maps": 0,
            "google":3,
            "yahoo": 2,
            "bing": 0
        })

    # Get Google ranking for the client URL
    s = serp_client.search(q=keyword, engine="google", google_domain="google.com", hl="en", gl="us")
    client_ranking_google = -1
    organic_results_list = s["organic_results"]
    for entry in organic_results_list:
        if client_url == urlparse(entry.get("link")).netloc:
            client_ranking_google = entry.get("position")
            break

    # Get Bing ranking for the client URL
    client_ranking_bing = -1
    s = serp_client.search(q=keyword, engine="bing", hl="en", gl="us")
    organic_results_list = s["organic_results"]
    for entry in organic_results_list:
        if client_url == urlparse(entry.get("link")).netloc:
            client_ranking_bing = entry.get("position")
            break

    # Get Yahoo ranking for the client URL
    client_ranking_yahoo = -1
    s = serp_client.search(p=keyword, engine="yahoo", hl="en", gl="us")
    organic_results_list = s["organic_results"]
    for entry in organic_results_list:
        if client_url == urlparse(entry.get("link")).netloc:
            client_ranking_yahoo = entry.get("position")
            break

    # Get Google Maps ranking for the client URL
    client_ranking_gmaps = -1
    s = serp_client.search(q=keyword, engine="google_maps", hl="en", gl="us")
    results_list = s["local_results"]
    for entry in results_list:
        if client_name == entry.get("title"):
            client_ranking_gmaps = entry.get("position")
            break

    data = {
            "keyword": client_name,
            "maps": client_ranking_gmaps,
            "google": client_ranking_google,
            "yahoo": client_ranking_yahoo,
            "bing": client_ranking_bing
    }

    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)