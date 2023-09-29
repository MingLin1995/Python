import aiohttp  # pip install aiohttp
import asyncio
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

BASE_URL = "https://fapi.binance.com/fapi/v1"

intervals = []


@app.route('/add_intervals', methods=['POST'])
def add_intervals_route():
    data = request.json
    intervals.extend(data)
    data = asyncio.run(main(data))
    return jsonify({"message": data})


@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")


# 成交量


async def fetch_volume(session):
    volume_url = f"{BASE_URL}/ticker/24hr"
    try:
        async with session.get(volume_url) as response:
            if response.status == 200:
                volume_info = await response.json()
                sorted_volume_info = sorted(volume_info, key=lambda volume: float(
                    volume.get("quoteVolume")), reverse=True)
                return sorted_volume_info
            else:
                return None
    except aiohttp.ClientError as e:
        print(f"Error: {e}")
        return None


# 判斷單位數


def format_volume(volume):
    volume_units = "億" if volume >= 100000000 else "萬"
    volume_formatted = volume / 100000000 if volume >= 100000000 else volume / 10000
    formatted_volume = "{:,.2f}".format(volume_formatted)
    return f"{formatted_volume}{volume_units}"


# 取得K線資料


async def fetch_klines(session, symbol, time_interval, limit):
    klines_url = f"{BASE_URL}/klines"
    params = {
        "symbol": symbol,
        "interval": time_interval,
        "limit": limit,
    }
    response = await session.get(klines_url, params=params)
    klines_data = await response.json()
    return [float(entry[4]) for entry in klines_data]

# 計算均線


class MovingAverageCalculator:
    def __init__(self, param, initial_data=None):
        self.param = param
        self.data = initial_data if initial_data is not None else []
        self.cumulative_sum = sum(self.data)

    def get_moving_average(self):
        if len(self.data) < self.param:  # 如果K線數量不足
            return None
        return self.cumulative_sum / self.param


# 均線比較


async def process_symbol(session, filter_params, symbol):

    time_interval = filter_params.time_interval
    param_1 = filter_params.param_1
    param_2 = filter_params.param_2
    param_3 = filter_params.param_3
    param_4 = filter_params.param_4
    comparison_operator_1 = filter_params.comparison_operator_1
    comparison_operator_2 = filter_params.comparison_operator_2
    logical_operator = filter_params.logical_operator

    klines_data1 = await fetch_klines(session, symbol, time_interval, param_1)
    klines_data2 = await fetch_klines(session, symbol, time_interval, param_2)
    ma_1 = MovingAverageCalculator(param_1, klines_data1)
    ma_2 = MovingAverageCalculator(param_2, klines_data2)
    ma_1_value = round(ma_1.get_moving_average(),
                       7) if ma_1.get_moving_average() is not None else None
    ma_2_value = round(ma_2.get_moving_average(),
                       7) if ma_2.get_moving_average() is not None else None

    # 沒被執行時等於None
    ma_3_value = None
    ma_4_value = None

    if param_3 is not None and param_4 is not None:
        klines_data3 = await fetch_klines(session, symbol, time_interval, param_3)
        klines_data4 = await fetch_klines(session, symbol, time_interval, param_4)
        ma_3 = MovingAverageCalculator(param_3, klines_data3)
        ma_4 = MovingAverageCalculator(param_4, klines_data4)
        ma_3_value = round(ma_3.get_moving_average(),
                           7) if ma_3.get_moving_average() is not None else None
        ma_4_value = round(ma_4.get_moving_average(),
                           7) if ma_4.get_moving_average() is not None else None

    if ma_1_value is not None and ma_2_value is not None:
        if ma_3_value is not None or ma_4_value is not None:
            condition = f"{ma_1_value} {comparison_operator_1} {ma_2_value} {logical_operator} {ma_3_value} {comparison_operator_2} {ma_4_value}"
        else:
            condition = f"{ma_1_value} {comparison_operator_1} {ma_2_value}"
        try:
            if eval(condition):
                return symbol
        except Exception as e:
            print(f"Error evaluating condition: {e}")

    return None

# 建立任務


async def apply_filter_parallel(session, filter_params, symbols):

    tasks = [
        process_symbol(session, filter_params, symbol)
        for symbol in symbols
    ]
    results = await asyncio.gather(*tasks)

    # 取出symbols不為None的值，再繼續篩選
    selected_symbols = [symbol for symbol in results if symbol is not None]

    return selected_symbols

# 建立物件


class FilterParameters:
    def __init__(self, time_interval, param_1, param_2, param_3, param_4,
                 comparison_operator_1, comparison_operator_2, logical_operator):
        self.time_interval = time_interval
        self.param_1 = param_1
        self.param_2 = param_2
        self.param_3 = param_3
        self.param_4 = param_4
        self.comparison_operator_1 = comparison_operator_1
        self.comparison_operator_2 = comparison_operator_2
        self.logical_operator = logical_operator


def get_filter_params(interval):
    return FilterParameters(
        time_interval=interval.get("time_interval"),
        param_1=interval.get("param_1"),
        param_2=interval.get("param_2"),
        param_3=interval.get("param_3"),
        param_4=interval.get("param_4"),
        comparison_operator_1=interval.get("comparison_operator_1"),
        comparison_operator_2=interval.get("comparison_operator_2"),
        logical_operator=interval.get("logical_operator")
    )


async def main(data):
    async with aiohttp.ClientSession() as session:
        intervals = data
        sorted_volume_info = await fetch_volume(session)
        # 轉換為字典
        symbol_info_dict = {entry["symbol"]
            : entry for entry in sorted_volume_info}
        # 取出symbol，建立列表
        symbols = list(symbol_info_dict.keys())

        selected_symbols = None

        for interval in intervals:
            filter_params = get_filter_params(interval)

            if filter_params.param_1 is None:
                continue

            if selected_symbols is None:
                selected_symbols = await apply_filter_parallel(session, filter_params, symbols)
            else:
                selected_symbols = await apply_filter_parallel(session, filter_params, selected_symbols)

        symbol_volume_data = get_symbol_volume_data(
            selected_symbols, symbol_info_dict)
        print(symbol_volume_data)
        print(len(symbol_volume_data), "筆資料")
    return symbol_volume_data

# 取的標的、成交量


def get_symbol_volume_data(selected_symbols, symbol_info_dict):
    symbol_volume_data = []

    # 使用字典解析一次性获取所有 selected_symbols 的数据
    symbol_volume_data = [
        {"標的": symbol, "成交量": format_volume(
            float(symbol_info_dict[symbol]["quoteVolume"]))}
        for symbol in selected_symbols if symbol in symbol_info_dict
    ]

    return symbol_volume_data


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
