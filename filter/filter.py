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


async def fetch_klines(session, symbol, time_interval):
    klines_url = f"{BASE_URL}/klines"
    params = {
        "symbol": symbol,
        "interval": time_interval,
        "limit": 365,
    }
    response = await session.get(klines_url, params=params)
    klines_data = await response.json()
    return [float(entry[4]) for entry in klines_data]

# 計算均線


class MovingAverageCalculator:
    def __init__(self, period):
        self.period = period
        self.data = []
        self.cumulative_sum = 0.0

    def add_data_point(self, value):
        self.data.append(value)
        self.cumulative_sum += value
        # 如果資料數量>時框，就扣掉最舊的一筆資料
        if len(self.data) > self.period:
            self.cumulative_sum -= self.data.pop(0)

    def get_moving_average(self):
        if len(self.data) < self.period:
            return None
        return self.cumulative_sum / self.period


async def process_symbol(session, symbol, time_interval, param_1, param_2, comparison_operator_1, param_3, param_4, comparison_operator_2, logical_operator):
    klines_data = await fetch_klines(session, symbol, time_interval)

    ma_1 = MovingAverageCalculator(param_1)
    ma_2 = MovingAverageCalculator(param_2)

    if param_3 is not None and param_4 is not None:
        ma_3 = MovingAverageCalculator(param_3)
        ma_4 = MovingAverageCalculator(param_4)

    for value in klines_data:
        ma_1.add_data_point(value)
        ma_2.add_data_point(value)
        if param_3 is not None and param_4 is not None:
            ma_3.add_data_point(value)
            ma_4.add_data_point(value)

    ma_1_value = round(ma_1.get_moving_average(),
                       7) if ma_1.get_moving_average() is not None else None
    ma_2_value = round(ma_2.get_moving_average(),
                       7) if ma_2.get_moving_average() is not None else None
    if param_3 is not None and param_4 is not None:
        ma_3_value = round(ma_3.get_moving_average(),
                           7) if ma_3.get_moving_average() is not None else None
        ma_4_value = round(ma_4.get_moving_average(),
                           7) if ma_4.get_moving_average() is not None else None

    # 沒被執行時等於None
    ma_3_value = None
    ma_4_value = None

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


async def apply_filter_parallel(session, time_interval, param_1, param_2, param_3, param_4, comparison_operator_1, comparison_operator_2, logical_operator, symbols):
    tasks = [
        process_symbol(session, symbol, time_interval, param_1, param_2, comparison_operator_1, param_3, param_4,
                       comparison_operator_2, logical_operator)
        for symbol in symbols
    ]
    results = await asyncio.gather(*tasks)

    # 取出symbols不為None的值繼續篩選
    selected_symbols = [symbol for symbol in results if symbol is not None]

    return selected_symbols


async def main(data):
    async with aiohttp.ClientSession() as session:
        intervals = data
        """  [
            {
                "time_interval": "15m",
                "param_1": 25,
                "param_2": 60,
                "param_3": None,
                "param_4": 99,
                "comparison_operator_1": ">",
                "comparison_operator_2": ">",
                "logical_operator": "and"
            },
            {
                "time_interval": "1h",
                "param_1": 25,
                "param_2": 60,
                "param_3": 60,
                "param_4": 99,
                "comparison_operator_1": ">",
                "comparison_operator_2": ">",
                "logical_operator": "and"
            },
            {
                "time_interval": "4h",
                "param_1": 25,
                "param_2": 60,
                "param_3": 60,
                "param_4": None,
                "comparison_operator_1": ">",
                "comparison_operator_2": ">",
                "logical_operator": "and"
            },
            {
                "time_interval": "1d",
                "param_1": None,
                "param_2": 60,
                "param_3": None,
                "param_4": 99,
                "comparison_operator_1": ">",
                "comparison_operator_2": ">",
                "logical_operator": "and"
            }
        ] """

        sorted_volume_info = await fetch_volume(session)

        # 轉換為字典
        symbol_info_dict = {entry["symbol"]: entry for entry in sorted_volume_info}

        # 從 symbol_info_dict 中提取符號列表
        symbols = list(symbol_info_dict.keys())
        """ symbols = [entry["symbol"] for entry in sorted_volume_info] """
        selected_symbols = None

        for interval in intervals:
            time_interval = interval.get("time_interval")
            param_1 = interval.get("param_1")
            param_2 = interval.get("param_2")
            param_3 = interval.get("param_3")
            param_4 = interval.get("param_4")
            comparison_operator_1 = interval.get("comparison_operator_1")
            comparison_operator_2 = interval.get("comparison_operator_2")
            logical_operator = interval.get("logical_operator")

            if param_1 is None:  # 如果沒有資料就跳過該層篩選
                continue

            if selected_symbols is None:
                selected_symbols = await apply_filter_parallel(session, time_interval, param_1, param_2, param_3, param_4, comparison_operator_1, comparison_operator_2, logical_operator, symbols)
            else:
                selected_symbols = await apply_filter_parallel(session, time_interval, param_1, param_2, param_3, param_4, comparison_operator_1, comparison_operator_2, logical_operator, selected_symbols)

        symbol_volume_data = []

        for symbol in selected_symbols:
            if symbol in symbol_info_dict:
                entry = symbol_info_dict[symbol]
                symbol_data = {"標的": symbol, "成交量": format_volume(
                    float(entry["quoteVolume"]))}
                symbol_volume_data.append(symbol_data)

        print(symbol_volume_data)
        print(len(symbol_volume_data), "筆資料")
    return symbol_volume_data


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
