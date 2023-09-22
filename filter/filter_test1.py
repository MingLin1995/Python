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


def calculate_moving_average(data, period):
    ma_sum = sum(data[-period:])
    return ma_sum / period


async def analyze_and_print_results(session, sorted_volume_info, interval_1, interval_2=None, interval_3=None, interval_4=None):
    tasks = []
    for entry in sorted_volume_info:
        symbol = entry.get("symbol")
        tasks.append(fetch_klines(session, symbol,
                     interval_1["time_interval"]))

    # 取得參數一的K線
    klines_results_interval_1 = await asyncio.gather(*tasks)

    results = []

    for entry, klines_data_interval_1 in zip(sorted_volume_info, klines_results_interval_1):
        symbol = entry.get("symbol")
        volume = entry.get("quoteVolume")
        formatted_volume = format_volume(float(volume))

        if interval_1["param_3"] != 0:
            if len(klines_data_interval_1) < interval_1["param_3"]:
                continue  # 跳過數據不足的標的

        # 參數一的均線
        group_ma_1_interval_1 = [
            round(calculate_moving_average(klines_data_interval_1, param), 7)
            for param in [interval_1["param_1"], interval_1["param_2"], interval_1["param_3"]]
            if param != 0
        ]

        if interval_1["param_3"] != 0:
            if eval(f"group_ma_1_interval_1[0] {interval_1['comparison_operator_1']} group_ma_1_interval_1[1] {interval_1['logical_operator']} group_ma_1_interval_1[1] {interval_1['comparison_operator_2']} group_ma_1_interval_1[2]"):
                if interval_2 is None:
                    result_dict = {
                        "標的": symbol,
                        "成交量": formatted_volume,

                    }
                    results.append(result_dict)
                else:
                    # 取得參數二的K線
                    klines_data_interval_2 = await fetch_klines(session, symbol, interval_2["time_interval"])

                    if interval_2["param_3"] != 0:
                        if len(klines_data_interval_2) < interval_2["param_3"]:
                            continue  # 跳過數據不足的標的

                    # 參數二的均線
                    group_ma_1_interval_2 = [
                        calculate_moving_average(
                            klines_data_interval_2, interval_2["param_1"]),
                        calculate_moving_average(
                            klines_data_interval_2, interval_2["param_2"]),
                        calculate_moving_average(
                            klines_data_interval_2, interval_2["param_3"]) if interval_2["param_3"] != 0 else None
                    ]
                    if interval_2["param_3"] != 0:
                        if eval(f"group_ma_1_interval_2[0] {interval_2['comparison_operator_1']} group_ma_1_interval_2[1] {interval_2['logical_operator']} group_ma_1_interval_2[1] {interval_2['comparison_operator_2']} group_ma_1_interval_2[2]"):
                            if interval_3 is None:
                                result_dict = {
                                    "標的": symbol,
                                    "成交量": formatted_volume,
                                }
                                results.append(result_dict)
                            else:
                                # 取得參數三的K線
                                klines_data_interval_3 = await fetch_klines(session, symbol, interval_3["time_interval"])

                                if interval_3["param_3"] != 0:
                                    if len(klines_data_interval_3) < interval_3["param_3"]:
                                        continue  # 跳過數據不足的標的

                                # 參數三的均線
                                group_ma_1_interval_3 = [
                                    calculate_moving_average(
                                        klines_data_interval_3, interval_3["param_1"]),
                                    calculate_moving_average(
                                        klines_data_interval_3, interval_3["param_2"]),
                                    calculate_moving_average(
                                        klines_data_interval_3, interval_3["param_3"]) if interval_3["param_3"] != 0 else None
                                ]

                                if interval_3["param_3"] != 0:
                                    if eval(f"group_ma_1_interval_3[0] {interval_3['comparison_operator_1']} group_ma_1_interval_3[1] {interval_3['logical_operator']} group_ma_1_interval_3[1] {interval_3['comparison_operator_2']} group_ma_1_interval_3[2]"):
                                        if interval_4 is None:
                                            result_dict = {
                                                "標的": symbol,
                                                "成交量": formatted_volume,
                                            }
                                            results.append(result_dict)
                                        else:
                                            # 取得參數四的K線
                                            klines_data_interval_4 = await fetch_klines(session, symbol, interval_4["time_interval"])

                                            if interval_4["param_3"] != 0:
                                                if len(klines_data_interval_4) < interval_4["param_3"]:
                                                    continue  # 跳過數據不足的標的

                                            # 參數四的均線
                                            group_ma_1_interval_4 = [
                                                calculate_moving_average(
                                                    klines_data_interval_4, interval_4["param_1"]),
                                                calculate_moving_average(
                                                    klines_data_interval_4, interval_4["param_2"]),
                                                calculate_moving_average(
                                                    klines_data_interval_4, interval_4["param_3"]) if interval_4["param_3"] != 0 else None
                                            ]

                                            if interval_4["param_3"] != 0:
                                                if eval(f"group_ma_1_interval_4[0] {interval_4['comparison_operator_1']} group_ma_1_interval_4[1] {interval_4['logical_operator']} group_ma_1_interval_4[1] {interval_4['comparison_operator_2']} group_ma_1_interval_4[2]"):
                                                    result_dict = {
                                                        "標的": symbol,
                                                        "成交量": formatted_volume,
                                                    }
                                                    results.append(result_dict)
                                            else:
                                                if eval(f"group_ma_1_interval_4[0] {interval_4['comparison_operator_1']} group_ma_1_interval_4[1]"):
                                                    result_dict = {
                                                        "標的": symbol,
                                                        "成交量": formatted_volume,
                                                    }
                                                    results.append(result_dict)
                                else:
                                    if eval(f"group_ma_1_interval_3[0] {interval_3['comparison_operator_1']} group_ma_1_interval_3[1]"):
                                        if interval_4 is None:
                                            result_dict = {
                                                "標的": symbol,
                                                "成交量": formatted_volume,
                                            }
                                            results.append(result_dict)
                                        else:
                                            # 取得參數四的K線
                                            klines_data_interval_4 = await fetch_klines(session, symbol, interval_4["time_interval"])

                                            if interval_4["param_3"] != 0:
                                                if len(klines_data_interval_4) < interval_4["param_3"]:
                                                    continue  # 跳過數據不足的標的

                                            # 參數四的均線
                                            group_ma_1_interval_4 = [
                                                calculate_moving_average(
                                                    klines_data_interval_4, interval_4["param_1"]),
                                                calculate_moving_average(
                                                    klines_data_interval_4, interval_4["param_2"]),
                                                calculate_moving_average(
                                                    klines_data_interval_4, interval_4["param_3"]) if interval_4["param_3"] != 0 else None
                                            ]

                                            if interval_4["param_3"] != 0:
                                                if eval(f"group_ma_1_interval_4[0] {interval_4['comparison_operator_1']} group_ma_1_interval_4[1] {interval_4['logical_operator']} group_ma_1_interval_4[1] {interval_4['comparison_operator_2']} group_ma_1_interval_4[2]"):
                                                    result_dict = {
                                                        "標的": symbol,
                                                        "成交量": formatted_volume,
                                                    }
                                                    results.append(result_dict)
                                            else:
                                                if eval(f"group_ma_1_interval_4[0] {interval_4['comparison_operator_1']} group_ma_1_interval_4[1]"):
                                                    result_dict = {
                                                        "標的": symbol,
                                                        "成交量": formatted_volume,
                                                    }
                                                    results.append(result_dict)
                    else:
                        if eval(f"group_ma_1_interval_2[0] {interval_2['comparison_operator_1']} group_ma_1_interval_2[1]"):
                            if interval_3 is None:
                                result_dict = {
                                    "標的": symbol,
                                    "成交量": formatted_volume,
                                }
                                results.append(result_dict)
                            else:
                                # 取得參數三的K線
                                klines_data_interval_3 = await fetch_klines(session, symbol, interval_3["time_interval"])

                                if interval_3["param_3"] != 0:
                                    if len(klines_data_interval_3) < interval_3["param_3"]:
                                        continue  # 跳過數據不足的標的

                                # 參數三的均線
                                group_ma_1_interval_3 = [
                                    calculate_moving_average(
                                        klines_data_interval_3, interval_3["param_1"]),
                                    calculate_moving_average(
                                        klines_data_interval_3, interval_3["param_2"]),
                                    calculate_moving_average(
                                        klines_data_interval_3, interval_3["param_3"]) if interval_3["param_3"] != 0 else None
                                ]

                                if interval_3["param_3"] != 0:
                                    if eval(f"group_ma_1_interval_3[0] {interval_3['comparison_operator_1']} group_ma_1_interval_3[1] {interval_3['logical_operator']} group_ma_1_interval_3[1] {interval_3['comparison_operator_2']} group_ma_1_interval_3[2]"):
                                        if interval_4 is None:
                                            result_dict = {
                                                "標的": symbol,
                                                "成交量": formatted_volume,
                                            }
                                            results.append(result_dict)
                                        else:
                                            # 取得參數四的K線
                                            klines_data_interval_4 = await fetch_klines(session, symbol, interval_4["time_interval"])

                                            if interval_4["param_3"] != 0:
                                                if len(klines_data_interval_4) < interval_4["param_3"]:
                                                    continue  # 跳過數據不足的標的

                                            # 參數四的均線
                                            group_ma_1_interval_4 = [
                                                calculate_moving_average(
                                                    klines_data_interval_4, interval_4["param_1"]),
                                                calculate_moving_average(
                                                    klines_data_interval_4, interval_4["param_2"]),
                                                calculate_moving_average(
                                                    klines_data_interval_4, interval_4["param_3"]) if interval_4["param_3"] != 0 else None
                                            ]

                                            if interval_4["param_3"] != 0:
                                                if eval(f"group_ma_1_interval_4[0] {interval_4['comparison_operator_1']} group_ma_1_interval_4[1] {interval_4['logical_operator']} group_ma_1_interval_4[1] {interval_4['comparison_operator_2']} group_ma_1_interval_4[2]"):
                                                    result_dict = {
                                                        "標的": symbol,
                                                        "成交量": formatted_volume,
                                                    }
                                                    results.append(result_dict)
                                            else:
                                                if eval(f"group_ma_1_interval_4[0] {interval_4['comparison_operator_1']} group_ma_1_interval_4[1]"):
                                                    result_dict = {
                                                        "標的": symbol,
                                                        "成交量": formatted_volume,
                                                    }
                                                    results.append(result_dict)
                                else:
                                    if eval(f"group_ma_1_interval_3[0] {interval_3['comparison_operator_1']} group_ma_1_interval_3[1]"):
                                        if interval_4 is None:
                                            result_dict = {
                                                "標的": symbol,
                                                "成交量": formatted_volume,
                                            }
                                            results.append(result_dict)
                                        else:
                                            # 取得參數四的K線
                                            klines_data_interval_4 = await fetch_klines(session, symbol, interval_4["time_interval"])

                                            if interval_4["param_3"] != 0:
                                                if len(klines_data_interval_4) < interval_4["param_3"]:
                                                    continue  # 跳過數據不足的標的

                                            # 參數四的均線
                                            group_ma_1_interval_4 = [
                                                calculate_moving_average(
                                                    klines_data_interval_4, interval_4["param_1"]),
                                                calculate_moving_average(
                                                    klines_data_interval_4, interval_4["param_2"]),
                                                calculate_moving_average(
                                                    klines_data_interval_4, interval_4["param_3"]) if interval_4["param_3"] != 0 else None
                                            ]

                                            if interval_4["param_3"] != 0:
                                                if eval(f"group_ma_1_interval_4[0] {interval_4['comparison_operator_1']} group_ma_1_interval_4[1] {interval_4['logical_operator']} group_ma_1_interval_4[1] {interval_4['comparison_operator_2']} group_ma_1_interval_4[2]"):
                                                    result_dict = {
                                                        "標的": symbol,
                                                        "成交量": formatted_volume,
                                                    }
                                                    results.append(result_dict)
                                            else:
                                                if eval(f"group_ma_1_interval_4[0] {interval_4['comparison_operator_1']} group_ma_1_interval_4[1]"):
                                                    result_dict = {
                                                        "標的": symbol,
                                                        "成交量": formatted_volume,
                                                    }
                                                    results.append(result_dict)
        else:
            if eval(f"group_ma_1_interval_1[0] {interval_1['comparison_operator_1']} group_ma_1_interval_1[1] "):
                if interval_2 is None:
                    result_dict = {
                        "標的": symbol,
                        "成交量": formatted_volume,
                    }
                    results.append(result_dict)
                else:
                    # 取得參數二的K線
                    klines_data_interval_2 = await fetch_klines(session, symbol, interval_2["time_interval"])

                    if interval_2["param_3"] != 0:
                        if len(klines_data_interval_2) < interval_2["param_3"]:
                            continue  # 跳過數據不足的標的

                    # 參數二的均線
                    group_ma_1_interval_2 = [
                        calculate_moving_average(
                            klines_data_interval_2, interval_2["param_1"]),
                        calculate_moving_average(
                            klines_data_interval_2, interval_2["param_2"]),
                        calculate_moving_average(
                            klines_data_interval_2, interval_2["param_3"]) if interval_2["param_3"] != 0 else None
                    ]
                    if interval_2["param_3"] != 0:
                        if eval(f"group_ma_1_interval_2[0] {interval_2['comparison_operator_1']} group_ma_1_interval_2[1] {interval_2['logical_operator']} group_ma_1_interval_2[1] {interval_2['comparison_operator_2']} group_ma_1_interval_2[2]"):
                            if interval_3 is None:
                                result_dict = {
                                    "標的": symbol,
                                    "成交量": formatted_volume,
                                }
                                results.append(result_dict)
                            else:
                                # 取得參數三的K線
                                klines_data_interval_3 = await fetch_klines(session, symbol, interval_3["time_interval"])

                                if interval_3["param_3"] != 0:
                                    if len(klines_data_interval_3) < interval_3["param_3"]:
                                        continue  # 跳過數據不足的標的

                                # 參數三的均線
                                group_ma_1_interval_3 = [
                                    calculate_moving_average(
                                        klines_data_interval_3, interval_3["param_1"]),
                                    calculate_moving_average(
                                        klines_data_interval_3, interval_3["param_2"]),
                                    calculate_moving_average(
                                        klines_data_interval_3, interval_3["param_3"]) if interval_3["param_3"] != 0 else None
                                ]

                                if interval_3["param_3"] != 0:
                                    if eval(f"group_ma_1_interval_3[0] {interval_3['comparison_operator_1']} group_ma_1_interval_3[1] {interval_3['logical_operator']} group_ma_1_interval_3[1] {interval_3['comparison_operator_2']} group_ma_1_interval_3[2]"):
                                        if interval_4 is None:
                                            result_dict = {
                                                "標的": symbol,
                                                "成交量": formatted_volume,
                                            }
                                            results.append(result_dict)
                                        else:
                                            # 取得參數四的K線
                                            klines_data_interval_4 = await fetch_klines(session, symbol, interval_4["time_interval"])

                                            if interval_4["param_3"] != 0:
                                                if len(klines_data_interval_4) < interval_4["param_3"]:
                                                    continue  # 跳過數據不足的標的

                                            # 參數四的均線
                                            group_ma_1_interval_4 = [
                                                calculate_moving_average(
                                                    klines_data_interval_4, interval_4["param_1"]),
                                                calculate_moving_average(
                                                    klines_data_interval_4, interval_4["param_2"]),
                                                calculate_moving_average(
                                                    klines_data_interval_4, interval_4["param_3"]) if interval_4["param_3"] != 0 else None
                                            ]

                                            if interval_4["param_3"] != 0:
                                                if eval(f"group_ma_1_interval_4[0] {interval_4['comparison_operator_1']} group_ma_1_interval_4[1] {interval_4['logical_operator']} group_ma_1_interval_4[1] {interval_4['comparison_operator_2']} group_ma_1_interval_4[2]"):
                                                    result_dict = {
                                                        "標的": symbol,
                                                        "成交量": formatted_volume,
                                                    }
                                                    results.append(result_dict)
                                            else:
                                                if eval(f"group_ma_1_interval_4[0] {interval_4['comparison_operator_1']} group_ma_1_interval_4[1]"):
                                                    result_dict = {
                                                        "標的": symbol,
                                                        "成交量": formatted_volume,
                                                    }
                                                    results.append(result_dict)
                                else:
                                    if eval(f"group_ma_1_interval_3[0] {interval_3['comparison_operator_1']} group_ma_1_interval_3[1]"):
                                        if interval_4 is None:
                                            result_dict = {
                                                "標的": symbol,
                                                "成交量": formatted_volume,
                                            }
                                            results.append(result_dict)
                                        else:
                                            # 取得參數四的K線
                                            klines_data_interval_4 = await fetch_klines(session, symbol, interval_4["time_interval"])

                                            if interval_4["param_3"] != 0:
                                                if len(klines_data_interval_4) < interval_4["param_3"]:
                                                    continue  # 跳過數據不足的標的

                                            # 參數四的均線
                                            group_ma_1_interval_4 = [
                                                calculate_moving_average(
                                                    klines_data_interval_4, interval_4["param_1"]),
                                                calculate_moving_average(
                                                    klines_data_interval_4, interval_4["param_2"]),
                                                calculate_moving_average(
                                                    klines_data_interval_4, interval_4["param_3"]) if interval_4["param_3"] != 0 else None
                                            ]

                                            if interval_4["param_3"] != 0:
                                                if eval(f"group_ma_1_interval_4[0] {interval_4['comparison_operator_1']} group_ma_1_interval_4[1] {interval_4['logical_operator']} group_ma_1_interval_4[1] {interval_4['comparison_operator_2']} group_ma_1_interval_4[2]"):
                                                    result_dict = {
                                                        "標的": symbol,
                                                        "成交量": formatted_volume,
                                                    }
                                                    results.append(result_dict)
                                            else:
                                                if eval(f"group_ma_1_interval_4[0] {interval_4['comparison_operator_1']} group_ma_1_interval_4[1]"):
                                                    result_dict = {
                                                        "標的": symbol,
                                                        "成交量": formatted_volume,
                                                    }
                                                    results.append(result_dict)
                    else:
                        if eval(f"group_ma_1_interval_2[0] {interval_2['comparison_operator_1']} group_ma_1_interval_2[1]"):
                            if interval_3 is None:
                                result_dict = {
                                    "標的": symbol,
                                    "成交量": formatted_volume,
                                }
                                results.append(result_dict)
                            else:
                                # 取得參數三的K線
                                klines_data_interval_3 = await fetch_klines(session, symbol, interval_3["time_interval"])

                                if interval_3["param_3"] != 0:
                                    if len(klines_data_interval_3) < interval_3["param_3"]:
                                        continue  # 跳過數據不足的標的

                                # 參數三的均線
                                group_ma_1_interval_3 = [
                                    calculate_moving_average(
                                        klines_data_interval_3, interval_3["param_1"]),
                                    calculate_moving_average(
                                        klines_data_interval_3, interval_3["param_2"]),
                                    calculate_moving_average(
                                        klines_data_interval_3, interval_3["param_3"]) if interval_3["param_3"] != 0 else None
                                ]

                                if interval_3["param_3"] != 0:
                                    if eval(f"group_ma_1_interval_3[0] {interval_3['comparison_operator_1']} group_ma_1_interval_3[1] {interval_3['logical_operator']} group_ma_1_interval_3[1] {interval_3['comparison_operator_2']} group_ma_1_interval_3[2]"):
                                        if interval_4 is None:
                                            result_dict = {
                                                "標的": symbol,
                                                "成交量": formatted_volume,
                                            }
                                            results.append(result_dict)
                                        else:
                                            # 取得參數四的K線
                                            klines_data_interval_4 = await fetch_klines(session, symbol, interval_4["time_interval"])

                                            if interval_4["param_3"] != 0:
                                                if len(klines_data_interval_4) < interval_4["param_3"]:
                                                    continue  # 跳過數據不足的標的

                                            # 參數四的均線
                                            group_ma_1_interval_4 = [
                                                calculate_moving_average(
                                                    klines_data_interval_4, interval_4["param_1"]),
                                                calculate_moving_average(
                                                    klines_data_interval_4, interval_4["param_2"]),
                                                calculate_moving_average(
                                                    klines_data_interval_4, interval_4["param_3"]) if interval_4["param_3"] != 0 else None
                                            ]

                                            if interval_4["param_3"] != 0:
                                                if eval(f"group_ma_1_interval_4[0] {interval_4['comparison_operator_1']} group_ma_1_interval_4[1] {interval_4['logical_operator']} group_ma_1_interval_4[1] {interval_4['comparison_operator_2']} group_ma_1_interval_4[2]"):
                                                    result_dict = {
                                                        "標的": symbol,
                                                        "成交量": formatted_volume,
                                                    }
                                                    results.append(result_dict)
                                            else:
                                                if eval(f"group_ma_1_interval_4[0] {interval_4['comparison_operator_1']} group_ma_1_interval_4[1]"):
                                                    result_dict = {
                                                        "標的": symbol,
                                                        "成交量": formatted_volume,
                                                    }
                                                    results.append(result_dict)
                                else:
                                    if eval(f"group_ma_1_interval_3[0] {interval_3['comparison_operator_1']} group_ma_1_interval_3[1]"):
                                        if interval_4 is None:
                                            result_dict = {
                                                "標的": symbol,
                                                "成交量": formatted_volume,
                                            }
                                            results.append(result_dict)
                                        else:
                                            # 取得參數四的K線
                                            klines_data_interval_4 = await fetch_klines(session, symbol, interval_4["time_interval"])

                                            if interval_4["param_3"] != 0:
                                                if len(klines_data_interval_4) < interval_4["param_3"]:
                                                    continue  # 跳過數據不足的標的

                                            # 參數四的均線
                                            group_ma_1_interval_4 = [
                                                calculate_moving_average(
                                                    klines_data_interval_4, interval_4["param_1"]),
                                                calculate_moving_average(
                                                    klines_data_interval_4, interval_4["param_2"]),
                                                calculate_moving_average(
                                                    klines_data_interval_4, interval_4["param_3"]) if interval_4["param_3"] != 0 else None
                                            ]

                                            if interval_4["param_3"] != 0:
                                                if eval(f"group_ma_1_interval_4[0] {interval_4['comparison_operator_1']} group_ma_1_interval_4[1] {interval_4['logical_operator']} group_ma_1_interval_4[1] {interval_4['comparison_operator_2']} group_ma_1_interval_4[2]"):
                                                    result_dict = {
                                                        "標的": symbol,
                                                        "成交量": formatted_volume,
                                                    }
                                                    results.append(result_dict)
                                            else:
                                                if eval(f"group_ma_1_interval_4[0] {interval_4['comparison_operator_1']} group_ma_1_interval_4[1]"):
                                                    result_dict = {
                                                        "標的": symbol,
                                                        "成交量": formatted_volume,
                                                    }
                                                    results.append(result_dict)

    return results


async def main():
    async with aiohttp.ClientSession() as session:
        interval_1 = {
            "time_interval": "15m",  # 用選單 幣安支援15種
            "param_1": 25,  # MA設定上限為1500MA
            "param_2": 60,
            "param_3": None,
            "comparison_operator_1": ">",  # 用選單 > >= < <=
            "comparison_operator_2": ">",
            "logical_operator": "and"  # 用選單 or and
        }

        if interval_1["param_3"] is None and interval_1["param_1"] is not None:  # 如果沒有輸入第三個參數，就改為0
            interval_1["param_3"] = 0

        interval_2 = {
            "time_interval": "1h",
            "param_1": 25,
            "param_2": 60,
            "param_3": 99,
            "comparison_operator_1": ">",
            "comparison_operator_2": ">",
            "logical_operator": "and"
        }

        if interval_2["param_3"] is None and interval_2["param_1"] is not None:
            interval_2["param_3"] = 0

        interval_3 = {
            "time_interval": "4h",
            "param_1": 25,
            "param_2": 60,
            "param_3": None,
            "comparison_operator_1": ">",
            "comparison_operator_2": ">",
            "logical_operator": "and"
        }

        if interval_3["param_3"] is None and interval_3["param_1"] is not None:
            interval_3["param_3"] = 0

        interval_4 = {
            "time_interval": "1d",
            "param_1": 25,
            "param_2": 60,
            "param_3": 99,
            "comparison_operator_1": ">",
            "comparison_operator_2": ">",
            "logical_operator": "and"
        }

        if interval_4["param_3"] is None and interval_4["param_1"] is not None:
            interval_4["param_3"] = 0

        sorted_volume_info = await fetch_volume(session)
        if interval_4["param_1"] == None:
            if interval_3["param_1"] == None:
                if interval_2["param_1"] == None:
                    results = await analyze_and_print_results(session, sorted_volume_info, interval_1)
                    if not results:
                        print("沒有符合的資料")
                    else:
                        print(results)
                        print(len(results), "筆資料")
                else:
                    results = await analyze_and_print_results(session, sorted_volume_info, interval_1, interval_2)
                    if not results:
                        print("沒有符合的資料")
                    else:
                        print(results)
            else:
                results = await analyze_and_print_results(session, sorted_volume_info, interval_1, interval_2, interval_3)
                if not results:
                    print("沒有符合的資料")
                else:
                    print(results)
        else:
            results = await analyze_and_print_results(session, sorted_volume_info, interval_1, interval_2, interval_3, interval_4)
            if not results:
                print("沒有符合的資料")
            else:
                print(results)

        """ results = await analyze_and_print_results(session, sorted_volume_info, interval_1, interval_2)
        print(results) """

if __name__ == "__main__":
    # 記錄程式碼開始執行的時間
    start_time = time.time()
    asyncio.run(main())

    # 記錄程式碼結束執行的時間
    end_time = time.time()

    # 計算執行時間
    execution_time = end_time - start_time

    print(f"程式碼執行時間：{execution_time:.4f} 秒")
