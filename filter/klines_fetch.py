# klines_fetch.py
from my_redis import load_data_from_redis, save_klines_data_to_redis
import requests
import concurrent.futures
import time
from apscheduler.schedulers.background import BackgroundScheduler


""" 更新K線資料 """


def update_symbol_klines_data(time_interval):
    symbol_quote_volume_data = load_data_from_redis()  # 從Redis取得標的資料
    if symbol_quote_volume_data is not None:
        symbols_klines_data = get_symbol_klines_data(
            symbol_quote_volume_data, time_interval)
        if symbols_klines_data is not None:
            save_klines_data_to_redis(
                symbols_klines_data, time_interval)  # 儲存K線資料到Redis
            print(f"更新 symbol_close_prices_data_{time_interval} 到 Redis",
                  time.strftime("%Y-%m-%d %H:%M:%S"))
        else:
            print(f"更新失敗，時間間隔：{time_interval}")
    else:
        print("無法獲得標的資料")


""" 取得K線資料資訊 """


def get_symbol_klines_data(symbol_quote_volume_data, time_interval):
    print("呼叫API！")
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        results = list(executor.map(fetch_klines_data, [
                       (entry['symbol'], time_interval) for entry in symbol_quote_volume_data]))
    return results


""" 取得幣安K線資料 """

BASE_URL = "https://fapi.binance.com/fapi/v1"


def fetch_klines_data(symbol_and_interval):
    symbol, time_interval = symbol_and_interval
    limit = 240
    klines_url = f"{BASE_URL}/klines"
    params = {
        "symbol": symbol,
        "interval": time_interval,
        "limit": limit,
    }
    try:
        response = requests.get(klines_url, params=params)
        if response.status_code == 200:
            klines_data = response.json()
            # 反轉數據
            klines_data.reverse()
            close_prices = [float(entry[4]) for entry in klines_data]

            data_to_store = {
                symbol: {"close_prices": close_prices}}
            return data_to_store

            # return {symbol: close_prices}
        else:
            print(
                f"Error fetching klines data for {symbol}: {response.status}")
            return None
    except Exception as e:
        print(f"Error: {symbol}: {e}")
        return None


""" 時框、更新頻率(分鐘) """
time_intervals = {
    # "1m": 1,
    # "3m": 3,
    "5m": 5,
    "15m": 15,
    "30m": 30,
    "1h": 60,
    "2h": 60*2,
    "4h": 60*4,
    "6h": 60*6,
    "8h": 60*8,
    "12h": 60*12,
    "1d": 60*24,
    "3d": 60*24,
    "1w": 60*24,
    "1M": 60*24,
}


if __name__ == "__main__":
    # 初始更新一次
    for time_interval in time_intervals:
        update_symbol_klines_data(time_interval)
        time.sleep(60)

    def job(time_interval):
        update_symbol_klines_data(time_interval)

    scheduler = BackgroundScheduler()
    for time_interval, update_frequency in time_intervals.items():
        scheduler.add_job(
            job, 'interval', minutes=update_frequency, args=[time_interval])

    scheduler.start()

    try:
        while True:
            time.sleep(60*5)  # 休眠減少CPU負擔
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
