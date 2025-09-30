import json
import os
from flask import Flask
from flask import jsonify
import requests
from flask import Response

CONTENT_TYPE = "application/json"

app = Flask(__name__)
def get_api_key():
    api_key = os.environ.get("YF_API_KEY")
    if api_key:
        return api_key
    else:
        with open("apiKeyDev.json") as f:
            return json.load(f)["apiKey"]


@app.route("/health", methods=['GET'])
def healthcheck():
    return jsonify({"status": "ok"}), 200

@app.route("/quote/<symbol>", methods=['GET'])
def quote(symbol):
    url = "https://yfapi.net/v6/finance/quote"
    querystring = {
        "symbols": symbol,
        "region": "PT",
        "lang": "en"
    }

    api_key = get_api_key()
    headers = {
        'X-API-KEY': api_key,
        'accept': CONTENT_TYPE,
        'User-Agent': '',
        'Accept-Encoding': '',
        'Connection': ''
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    data = json.loads(response.content)

    def handle_limit_reached(data):
        if "message" in data:
            print(429, 'Daily request limit reached')
            return Response(response='Daily request limit reached', status=429, mimetype=CONTENT_TYPE)
        return None

    def handle_symbol_not_found(data):
        if ("quoteResponse" not in data) or (data["quoteResponse"] is None):
            print(404, 'Symbol not found')
            return Response(response='Symbol not found', status=404, mimetype=CONTENT_TYPE)
        return None

    def build_quote_response(result):
        if len(result) == 0:
            print(404, "Symbol not found")
            return Response(response="Symbol not found", status=404, mimetype=CONTENT_TYPE)
        i = result[0]
        ln = i.get("longName", "") if i.get("longName") is not None else ""
        dictionary = {
            "currency": i.get("currency", ""),
            "shortMarket": i.get("exchange", ""),
            "market": i.get("fullExchangeName", ""),
            "shortName": i.get("shortName", ""),
            "name": ln,
            "price": i.get("regularMarketPrice", ""),
            "symbol": i.get("symbol", "")
        }
        json_object = json.dumps(dictionary, indent=4)
        return Response(response=json_object, status=200, mimetype=CONTENT_TYPE)

    limit_response = handle_limit_reached(data)
    if limit_response:
        return limit_response

    not_found_response = handle_symbol_not_found(data)
    if not_found_response:
        return not_found_response

    quote = data["quoteResponse"]
    result = quote.get("result", [])
    return build_quote_response(result)


if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=True, port=5000)
