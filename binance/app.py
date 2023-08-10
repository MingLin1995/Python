from flask import Flask, render_template, request
import requests

app = Flask(__name__)


def calculate_moving_average(data, period):
    ma_sum = sum(data[-period:])
    return ma_sum / period


def format_volume(volume):
    if volume >= 100_000_000:
        volume_units = "億"
        volume_formatted = volume / 100_000_000
    else:
        volume_units = "萬"
        volume_formatted = volume / 10_000

    formatted_volume = "{:,.2f}".format(volume_formatted)
    return f"{formatted_volume}{volume_units}"


def get_contract_volume(num_pairs):
    base_url = "https://fapi.binance.com/fapi/v1"

    exchange_info_url = f"{base_url}/exchangeInfo"
    exchange_info = requests.get(exchange_info_url).json()
    contract_trading_pairs = [symbol['symbol']
                              for symbol in exchange_info['symbols'] if symbol['contractType'] == "PERPETUAL"]

    usdt_contract_volumes = {}

    for pair in contract_trading_pairs:
        if pair.endswith("USDT"):
            ticker_url = f"{base_url}/ticker/24hr"
            params = {"symbol": pair}
            ticker_data = requests.get(ticker_url, params=params).json()

            if 'quoteVolume' in ticker_data:
                volume_24h = float(ticker_data['quoteVolume'])
                usdt_contract_volumes[pair] = volume_24h

    sorted_volumes = sorted(usdt_contract_volumes.items(),
                            key=lambda x: x[1], reverse=True)
    top_pairs = [pair for pair, _ in sorted_volumes[:num_pairs]]

    return top_pairs


def find_pairs_with_condition(pairs, interval, ma_25, ma_99, comparison_operator):
    selected_pairs = []

    for pair in pairs:
        klines_url = f"https://fapi.binance.com/fapi/v1/klines"
        params = {
            "symbol": pair,
            "interval": interval,
            "limit": 100,
        }
        klines_data = requests.get(klines_url, params=params).json()

        if len(klines_data) >= ma_99:
            close_prices = [float(entry[4]) for entry in klines_data]
            ma_25_value = calculate_moving_average(close_prices, ma_25)
            ma_99_value = calculate_moving_average(close_prices, ma_99)

            ma_25_formatted = "{:,.7f}".format(ma_25_value)
            ma_99_formatted = "{:,.7f}".format(ma_99_value)

            if comparison_operator == "greater":
                if ma_25_value > ma_99_value:
                    selected_pairs.append(
                        (pair, ma_25_formatted, ma_99_formatted))
            elif comparison_operator == "less":
                if ma_25_value < ma_99_value:
                    selected_pairs.append(
                        (pair, ma_25_formatted, ma_99_formatted))

    return selected_pairs


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        interval = request.form.get('interval')
        num_pairs = int(request.form.get('num_pairs'))
        ma_25 = int(request.form.get('ma_25'))
        ma_99 = int(request.form.get('ma_99'))
        # Get comparison operator from user input
        comparison_operator = request.form.get('comparison_operator')

        top_contract_pairs = get_contract_volume(num_pairs)
        selected_pairs = find_pairs_with_condition(
            top_contract_pairs, interval, ma_25, ma_99, comparison_operator)

        usdt_contract_volumes = {}
        for pair in top_contract_pairs:
            ticker_url = f"https://fapi.binance.com/fapi/v1/ticker/24hr"
            params = {"symbol": pair}
            ticker_data = requests.get(ticker_url, params=params).json()
            if 'quoteVolume' in ticker_data:
                volume_24h = float(ticker_data['quoteVolume'])
                formatted_volume = format_volume(
                    volume_24h)  # Format the volume
                # Store the formatted volume
                usdt_contract_volumes[pair] = formatted_volume

        return render_template('index.html', selected_pairs=selected_pairs, usdt_contract_volumes=usdt_contract_volumes)

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
