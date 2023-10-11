# MA.py
from my_redis import load_klines_data_from_redis
import numpy as np


""" 取得特定時框K線資料 """


def process_interval(intervals):
    time_interval = intervals['time_interval']

    # 代表該時框沒有參數
    if intervals["param_1"] is not None:
        # 取得該時框所有標的的K線資料
        data = load_klines_data_from_redis(time_interval)
        # print(data[0]["BTCUSDT"]["quote_volume"])
        # 計算MA
        ma_results = calculate_ma(data, intervals)
        return time_interval, ma_results
    return None


""" MA計算 """


def calculate_ma(data, intervals):
    results = []

    params = [intervals[f'param_{i}']
              for i in range(1, 5)]  # 取得 param_1 到 param_4 的值

    for symbol_data in data:
        symbol, quoteVolume_close_prices = symbol_data.popitem()

        # 提取出close_prices列表
        close_prices = quoteVolume_close_prices['close_prices']
        close_prices = np.array(close_prices)  # 转换为NumPy数组

        max_param = max(param for param in params if param is not None)
        # 資料長度不足以計算MA就跳過該標的
        if len(close_prices) < max_param:
            # print(f"K線資料不足以計算 {symbol} 的均線")
            continue

        ma_data = {}
        for param in params:
            if param is not None:
                # print(f" {symbol} 的 {param} 有參數")
                ma = np.mean(close_prices[:param])
                ma_str = "{:.7f}".format(ma)  # 小數點第七位
                ma_data[f'MA_{param}'] = float(ma_str)
            else:
                # print(f" {symbol} 的 {param} 沒有參數")
                continue

        if compare_ma_values(ma_data, intervals):
            results.append(symbol)
            # print(symbol, intervals["time_interval"], ma_data)
    return results


""" MA篩選 """


def compare_ma_values(ma_data, intervals):
    param_1 = intervals['param_1']
    param_2 = intervals['param_2']
    param_3 = intervals['param_3']
    param_4 = intervals['param_4']
    comparison_operator_1 = intervals['comparison_operator_1']
    comparison_operator_2 = intervals['comparison_operator_2']
    logical_operator = intervals['logical_operator']

    ma_1 = float(ma_data[f'MA_{param_1}'])
    ma_2 = float(ma_data[f'MA_{param_2}'])

    if param_3 is None or param_4 is None:
        condition = bool(eval(f'{ma_1} {comparison_operator_1} {ma_2}'))
    else:
        ma_3 = float(ma_data[f'MA_{param_3}'])
        ma_4 = float(ma_data[f'MA_{param_4}'])

        # 執行比較並檢查條件
        condition_1 = bool(eval(f'{ma_1} {comparison_operator_1} {ma_2}'))
        condition_2 = bool(eval(f'{ma_3} {comparison_operator_2} {ma_4}'))

        # 使用邏輯運算符進行條件組合
        if logical_operator == 'and':
            condition = condition_1 and condition_2
        elif logical_operator == 'or':
            condition = condition_1 or condition_2

    if condition:  # 符合篩選條件
        return True
    else:
        return None
