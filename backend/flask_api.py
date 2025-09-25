from flask import Flask, jsonify, request
from flask_cors import CORS
import serpapi
import redis
import json
from urllib.parse import urlencode, quote_plus
import random

# importing os module for environment variables
import os

from urllib.parse import urlparse

app = Flask(__name__)
CORS(app)

cache = redis.Redis(host="redis", port=6379, decode_responses=True)

# The SERP_KEY is loaded from the environment variable which is set by docker-compose.
serp_client = serpapi.Client(api_key=os.getenv("SERP_KEY"))
CACHE_TTL = 604800  # This sets how long the cache will hold the data (in seconds) (1 week)


def cache_response(ttl=CACHE_TTL):
    """Decorator to cache view results in Redis."""
    def decorator(f):
        def wrapper(*args, **kwargs):
            refresh = (request.args.get("refresh") == "true") # The request query parameter forces a refresh of the cached data.
            # Create a unique cache key from URL path + sorted query params
            allowed_keys = ["client_name", "client_url", "keyword", "source", "client_location", "client_coordinates"]
            filtered_args = {k: request.args[k] for k in allowed_keys if k in request.args}
            cache_key = f"{request.path}:{json.dumps(filtered_args, sort_keys=True)}"
            if not refresh:
                try:
                    # Check if cached
                    cached_data = cache.get(cache_key)
                    # If cached data exists and refresh is not requested, return cached data
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
    client_location = request.args.get("client_location")
    client_coordinates = request.args.get("client_coordinates")
    gmaps_name = request.args.get("gmaps_name")
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

        if client_location:
            params["location"] = client_location

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

        if client_location:
            params["location"] = client_location

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

        if client_coordinates:
            params["ll"] = client_coordinates
            reference_url = f"https://www.google.com/maps/search/{quote_plus(params['q'])}/{params['ll']}"

        else:
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
                if gmaps_name == entry.get("title", ""):
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
