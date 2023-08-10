from flask import Flask, render_template, request
import asyncio
import aiohttp

app = Flask(__name__)

BASE_URL = "https://fapi.binance.com/fapi/v1"


async def fetch_ticker(session, pair):
    async with session.get(f"{BASE_URL}/ticker/24hr", params={"symbol": pair}) as response:
        ticker_data = await response.json()
        return pair, float(ticker_data.get('quoteVolume', 0))


async def fetch_klines(session, pair, interval):
    async with session.get(f"{BASE_URL}/klines", params={"symbol": pair, "interval": interval, "limit": 100}) as response:
        klines_data = await response.json()
        return [float(entry[4]) for entry in klines_data]


@app.route('/', methods=['GET', 'POST'])
async def index():
    if request.method == 'POST':
        interval = request.form.get('interval')
        ma_25 = int(request.form.get('ma_25'))
        ma_99 = int(request.form.get('ma_99'))
        comparison_operator = request.form.get('comparison_operator')

        async with aiohttp.ClientSession() as session:
            exchange_info = await fetch_exchange_info(session)
            contract_trading_pairs = get_contract_trading_pairs(exchange_info)

            ticker_results = await fetch_ticker_data(session, contract_trading_pairs)
            usdt_contract_volumes = calculate_ticker_volumes(ticker_results)

            selected_pairs = await find_selected_pairs(session, usdt_contract_volumes.keys(), interval, ma_25, ma_99, comparison_operator)

            return render_template('index2.html', selected_pairs=selected_pairs, usdt_contract_volumes=usdt_contract_volumes)
    return render_template('index2.html')

# 子功能1: 獲取交易所信息


async def fetch_exchange_info(session):
    async with session.get(f"{BASE_URL}/exchangeInfo") as response:
        exchange_info = await response.json()
        return exchange_info

# 子功能2: 根據交易所信息，獲取符合條件的交易對


def get_contract_trading_pairs(exchange_info):
    return [symbol['symbol'] for symbol in exchange_info['symbols'] if symbol['contractType'] == "PERPETUAL" and symbol['symbol'].endswith("USDT")]

# 子功能3: 批量獲取交易對的 24 小時內交易資料


async def fetch_ticker_data(session, pairs):
    tasks = [fetch_ticker(session, pair) for pair in pairs]
    return await asyncio.gather(*tasks)

# 子功能4: 計算交易對的成交量


def calculate_ticker_volumes(ticker_results):
    return {pair: format_volume(volume) for pair, volume in ticker_results if volume > 0}

# 子功能5: 根據指定條件，找到選定的交易對


async def find_selected_pairs(session, pairs, interval, ma_25, ma_99, comparison_operator):
    tasks = [fetch_klines(session, pair, interval) for pair in pairs]
    klines_results = await asyncio.gather(*tasks)

    selected_pairs = []
    for pair, klines_data in zip(pairs, klines_results):
        if len(klines_data) >= ma_99:
            ma_25_value = calculate_moving_average(klines_data[-ma_25:], ma_25)
            ma_99_value = calculate_moving_average(klines_data[-ma_99:], ma_99)

            if (comparison_operator == "greater" and ma_25_value > ma_99_value) or (comparison_operator == "less" and ma_25_value < ma_99_value):
                selected_pairs.append((pair, "{:,.7f}".format(
                    ma_25_value), "{:,.7f}".format(ma_99_value)))

    return selected_pairs


def calculate_moving_average(data, period):
    ma_sum = sum(data)
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


if __name__ == '__main__':
    app.run(debug=True)
