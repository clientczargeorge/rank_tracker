from flask import Flask, jsonify, request
from flask_cors import CORS
import serpapi
import redis
import json
from urllib.parse import urlencode, quote_plus
import random

# importing os module for environment variables
import os
# importing necessary functions from dotenv library
from dotenv import load_dotenv, dotenv_values

from urllib.parse import urlparse

app = Flask(__name__)
CORS(app)

# loading variables from .env file
load_dotenv()

cache = redis.Redis(host="redis", port=6379, decode_responses=True)


serp_client = serpapi.Client(api_key=os.getenv("SERP_KEY"))
CACHE_TTL = 3600  # This sets how long the cache will hold the data (in seconds)


def cache_response(ttl=CACHE_TTL):
    """Decorator to cache view results in Redis."""
    def decorator(f):
        def wrapper(*args, **kwargs):
            try:
                # Create a unique cache key from URL path + sorted query params
                cache_key = f"{request.path}:{json.dumps(request.args, sort_keys=True)}"

                # Check if cached
                cached_data = cache.get(cache_key)
                if cached_data:
                    return jsonify(json.loads(cached_data))
            except KeyError:
                # Ignore key errors and proceed as if no cache
                pass

            # Call the original function
            result = f(*args, **kwargs)

            try:
                # Store in Redis with TTL
                cache.setex(cache_key, ttl, json.dumps(result.get_json()))
            except KeyError:
                # Ignore key errors during cache set
                pass

            return result
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

@app.route('/api')
@cache_response()
def serp_results():
    client_url = request.args.get("client_url")
    client_name = request.args.get("client_name")
    keyword = request.args.get("keyword")
    source = request.args.get("source")

    debug = (request.args.get("debug") == "true")

    if source == "google":
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

        try:
            s = serp_client.search(**params)
            organic_results_list = s.get("organic_results", [])
            for entry in organic_results_list:
                if client_url == urlparse(entry.get("link", "")).netloc:
                    client_ranking_google = entry.get("position", -1)
                    return jsonify({
                        "google": client_ranking_google,
                        "reference_url": reference_url,
                    })
            return jsonify({
                "google": -1,
                "reference_url": reference_url,
            })
        except Exception as e:
            # Log error e if you want
            return jsonify({
                "google": -1,
                "reference_url": reference_url,
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

        try:
            s = serp_client.search(**params)
            organic_results_list = s.get("organic_results", [])
            for entry in organic_results_list:
                if client_url == urlparse(entry.get("link", "")).netloc:
                    client_ranking_bing = entry.get("position", -1)
                    return jsonify({
                        "bing": client_ranking_bing,
                        "reference_url": reference_url,
                    })
            return jsonify({
                "bing": -1,
                "reference_url": reference_url,
            })
        except Exception as e:
            # Log error e if you want
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

        try:
            s = serp_client.search(**params)
            organic_results_list = s.get("organic_results", [])
            for entry in organic_results_list:
                if client_url == urlparse(entry.get("link", "")).netloc:
                    client_ranking_yahoo = entry.get("position", -1)
                    return jsonify({
                        "yahoo": client_ranking_yahoo,
                        "reference_url": reference_url,
                    })
            return jsonify({
                "yahoo": -1,
                "reference_url": reference_url,
            })
        except Exception as e:
            # Log error e if you want
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

        try:
            s = serp_client.search(**params)
            results_list = s.get("local_results", [])
            for entry in results_list:
                if client_name == entry.get("title", ""):
                    client_ranking_gmaps = entry.get("position", -1)
                    return jsonify({
                        "gmaps": client_ranking_gmaps,
                        "reference_url": reference_url,
                    })
            return jsonify({
                "gmaps": -1,
                "reference_url": reference_url,
            })
        except Exception as e:
            # Log error e if you want
            return jsonify({
                "gmaps": -1,
                "reference_url": reference_url,
            })

    return jsonify({"error": "Invalid source"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)