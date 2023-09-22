import aiohttp
import asyncio
from flask import Flask, render_template
import time


BASE_URL = "https://fapi.binance.com/fapi/v1"


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
    if volume >= 100000000:
        volume_units = "億"
        volume_formatted = volume / 100000000
    else:
        volume_units = "萬"
        volume_formatted = volume / 10000
    formatted_volume = "{:,.2f}".format(volume_formatted)  # 成交量取到小數點第二位
    return f"{formatted_volume}{volume_units}"

# 取得K線資料


async def fetch_klines(session, symbol, time_interval):
    klines_url = f"{BASE_URL}/klines"
    params = {
        "symbol": symbol,
        "interval": time_interval,
        "limit": 240,
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
        if len(self.data) > self.period:
            self.cumulative_sum -= self.data.pop(0)

    def get_moving_average(self):
        if len(self.data) < self.period:
            return None
        return self.cumulative_sum / self.period


async def apply_filter(session, time_interval, param_1, param_2, param_3, comparison_operator_1, comparison_operator_2, logical_operator,  symbols=None, selected_symbols=None):

    if param_3 is not None:
        if symbols is not None:
            filtered_symbols = []
            for symbol in symbols:
                klines_data = await fetch_klines(session, symbol, time_interval)

                ma_1 = MovingAverageCalculator(param_1)
                ma_2 = MovingAverageCalculator(param_2)
                ma_3 = MovingAverageCalculator(param_3)

                for value in klines_data:
                    ma_1.add_data_point(value)
                    ma_2.add_data_point(value)
                    ma_3.add_data_point(value)

                ma_1_value = round(ma_1.get_moving_average(
                ), 7) if ma_1.get_moving_average() is not None else None
                ma_2_value = round(ma_2.get_moving_average(
                ), 7) if ma_2.get_moving_average() is not None else None
                ma_3_value = round(ma_3.get_moving_average(
                ), 7) if ma_3.get_moving_average() is not None else None

                if ma_1_value is not None and ma_2_value is not None and ma_3_value is not None:
                    condition = f"{ma_1_value} {comparison_operator_1} {ma_2_value} {logical_operator} {ma_2_value} {comparison_operator_2} {ma_3_value}"
                    try:
                        if eval(condition):
                            filtered_symbols.append(symbol)
                    except Exception as e:
                        print(f"Error evaluating condition: {e}")

            return filtered_symbols
        else:
            filtered_symbols = []
            for symbol in selected_symbols:
                klines_data = await fetch_klines(session, symbol, time_interval)
                ma_1 = MovingAverageCalculator(param_1)
                ma_2 = MovingAverageCalculator(param_2)
                ma_3 = MovingAverageCalculator(param_3)

                for value in klines_data:
                    ma_1.add_data_point(value)
                    ma_2.add_data_point(value)
                    ma_3.add_data_point(value)

                ma_1_value = round(ma_1.get_moving_average(
                ), 7) if ma_1.get_moving_average() is not None else None
                ma_2_value = round(ma_2.get_moving_average(
                ), 7) if ma_2.get_moving_average() is not None else None
                ma_3_value = round(ma_3.get_moving_average(
                ), 7) if ma_3.get_moving_average() is not None else None

                if ma_1_value is not None and ma_2_value is not None and ma_3_value is not None:
                    condition = f"{ma_1_value} {comparison_operator_1} {ma_2_value} {logical_operator} {ma_2_value} {comparison_operator_2} {ma_3_value}"

                    try:
                        if eval(condition):
                            filtered_symbols.append(symbol)
                    except Exception as e:
                        print(f"Error evaluating condition: {e}")

            return filtered_symbols
    else:
        if symbols is not None:
            filtered_symbols = []

            for symbol in symbols:
                klines_data = await fetch_klines(session, symbol, time_interval)

                ma_1 = MovingAverageCalculator(param_1)
                ma_2 = MovingAverageCalculator(param_2)

                for value in klines_data:
                    ma_1.add_data_point(value)
                    ma_2.add_data_point(value)

                ma_1_value = round(ma_1.get_moving_average(
                ), 7) if ma_1.get_moving_average() is not None else None
                ma_2_value = round(ma_2.get_moving_average(
                ), 7) if ma_2.get_moving_average() is not None else None

                if ma_1_value is not None and ma_2_value is not None:
                    condition = f"{ma_1_value} {comparison_operator_1} {ma_2_value}"
                    try:
                        if eval(condition):
                            filtered_symbols.append(symbol)
                    except Exception as e:
                        print(f"Error evaluating condition: {e}")

            return filtered_symbols
        else:
            filtered_symbols = []
            for symbol in selected_symbols:
                klines_data = await fetch_klines(session, symbol, time_interval)

                ma_1 = MovingAverageCalculator(param_1)
                ma_2 = MovingAverageCalculator(param_2)

                for value in klines_data:
                    ma_1.add_data_point(value)
                    ma_2.add_data_point(value)

                ma_1_value = round(ma_1.get_moving_average(
                ), 7) if ma_1.get_moving_average() is not None else None
                ma_2_value = round(ma_2.get_moving_average(
                ), 7) if ma_2.get_moving_average() is not None else None

                if ma_1_value is not None and ma_2_value is not None:
                    condition = f"{ma_1_value} {comparison_operator_1} {ma_2_value}"

                    try:
                        if eval(condition):
                            filtered_symbols.append(symbol)
                    except Exception as e:
                        print(f"Error evaluating condition: {e}")

            return filtered_symbols


async def main():
    async with aiohttp.ClientSession() as session:
        intervals = [
            {
                "time_interval": "15m",
                "param_1": 25,
                "param_2": 60,
                "param_3": None,
                "comparison_operator_1": ">",
                "comparison_operator_2": ">",
                "logical_operator": "and"
            },
            {
                "time_interval": "1h",
                "param_1": 25,
                "param_2": 60,
                "param_3": 99,
                "comparison_operator_1": ">",
                "comparison_operator_2": ">",
                "logical_operator": "and"
            },
            {
                "time_interval": "4h",
                "param_1": 25,
                "param_2": 60,
                "param_3": None,
                "comparison_operator_1": ">",
                "comparison_operator_2": ">",
                "logical_operator": "and"
            },
            {
                "time_interval": "1d",
                "param_1": 25,
                "param_2": 60,
                "param_3": 99,
                "comparison_operator_1": ">",
                "comparison_operator_2": ">",
                "logical_operator": "and"
            }
        ]

        sorted_volume_info = await fetch_volume(session)
        symbols = [entry["symbol"] for entry in sorted_volume_info]
        selected_symbols = None
        for i, interval in enumerate(intervals, start=1):
            time_interval = interval.get("time_interval")
            param_1 = interval.get("param_1")
            param_2 = interval.get("param_2")
            param_3 = interval.get("param_3")
            comparison_operator_1 = interval.get("comparison_operator_1")
            comparison_operator_2 = interval.get("comparison_operator_2")
            logical_operator = interval.get("logical_operator")

            if param_1 is None:
                continue

            if selected_symbols is None:
                selected_symbols = await apply_filter(session, time_interval, param_1, param_2, param_3, comparison_operator_1, comparison_operator_2, logical_operator, symbols)
            else:
                selected_symbols = await apply_filter(session, time_interval, param_1, param_2, param_3, comparison_operator_1, comparison_operator_2, logical_operator, selected_symbols)

        symbol_volume_data = []

        for symbol in selected_symbols:
            for entry in sorted_volume_info:
                if entry["symbol"] == symbol:
                    symbol_data = {"標的": symbol, "成交量": format_volume(
                        float(entry["quoteVolume"]))}
                    symbol_volume_data.append(symbol_data)
                    break

        print(symbol_volume_data)
        print(len(symbol_volume_data), "筆資料")


if __name__ == "__main__":
    # 記錄程式碼開始執行的時間
    start_time = time.time()
    asyncio.run(main())
    # 記錄程式碼結束執行的時間
    end_time = time.time()
    # 計算執行時間
    execution_time = end_time - start_time
    print(f"程式碼執行時間：{execution_time:.4f} 秒")
