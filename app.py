from flask import Flask, render_template, request, jsonify
import requests
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)

# Replace with your actual API keys and URLs
FINANCE_SEARCH_API_URL = 'https://api.polygon.io/v3/reference/tickers?search='
FINANCE_API_KEY = os.getenv('FINANCE_API_KEY')
FINANCE_API_URL_TEMPLATE = 'https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/2023-01-09/2023-01-09?apiKey={apiKey}'
GEMINI_API_URL = 'https://api.gemini.com/v1/pricefeed'
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    keyword = request.args.get('keyword')
    if not keyword:
        return jsonify({'error': 'No keyword provided.'})

    response = requests.get(f"{FINANCE_SEARCH_API_URL}{keyword}&apiKey={FINANCE_API_KEY}")
    if response.status_code != 200:
        return jsonify({'error': 'Error fetching search results.'})
    data = response.json()

    if "results" not in data:
        return jsonify({'error': 'No matches found.'})

    matches = data['results']
    companies = [{'symbol': match['ticker'], 'name': match['name']} for match in matches]

    return jsonify(companies)

@app.route('/predict', methods=['GET'])
def predict():
    symbols = request.args.get('symbols')
    if not symbols:
        return jsonify({'error': 'No company symbols provided.'})

    symbols_list = symbols.split(',')

    company_data = []
    for symbol in symbols_list:
        url = FINANCE_API_URL_TEMPLATE.format(symbol=symbol, apiKey=FINANCE_API_KEY)
        response = requests.get(url)
        if response.status_code != 200:
            return jsonify({'error': f'Error fetching stock price for {symbol}.'})
        data = response.json()

        if "results" not in data:
            return jsonify({'error': f'Invalid company symbol: {symbol}.'})

        latest_price_data = data['results'][0]
        current_price = latest_price_data['c']

        company_data.append({
            'symbol': symbol.upper(),
            'currentPrice': current_price
        })

    # Fetch Gemini API response
    gemini_response = requests.get(GEMINI_API_URL)
    if gemini_response.status_code == 200:
        gemini_data = gemini_response.json()
    else:
        gemini_data = {'error': 'Error fetching Gemini data'}

    # Dummy prediction logic for illustration
    prediction = "Comparing stock prices."
    if len(company_data) > 1:
        sorted_data = sorted(company_data, key=lambda x: x['currentPrice'], reverse=True)
        prediction = f"{sorted_data[0]['symbol']} has the highest current stock price."

    # Generate a text summary
    summary = f"The stock prices for the selected companies are:\n"
    for company in company_data:
        summary += f"{company['symbol']}: ${company['currentPrice']}\n"
    summary += f"\nPrediction: {prediction}"

    return jsonify({
        'companies': company_data,
        'prediction': prediction,
        'geminiData': gemini_data,
        'summary': summary
    })

if __name__ == '__main__':
    app.run(debug=True)
