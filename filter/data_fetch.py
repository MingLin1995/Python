# data_fetch.py
import requests
from my_redis import save_data_to_redis
import time
# pip install apscheduler
from apscheduler.schedulers.background import BackgroundScheduler


""" 更新標的、成交量資料 """


def update_symbol_quote_volume_data():
    symbol_quote_volume_data = fetch_24hr_data()  # 取得幣安API資料
    if symbol_quote_volume_data is not None:
        save_data_to_redis(symbol_quote_volume_data)  # 儲存到Redis
        """ print("更新 symbol_quote_volume_data 到 Redis",
              time.strftime("%Y-%m-%d %H:%M:%S")) """
    else:
        print("更新失敗")


""" 取得幣安API資料 """
BASE_URL = "https://fapi.binance.com/fapi/v1"


def fetch_24hr_data():
    symbol_quote_volume_data = []
    volume_url = f"{BASE_URL}/ticker/24hr"
    try:
        response = requests.get(volume_url)
        # print(response.status_code)
        if response.status_code == 200:
            # print("呼叫API！")
            data_24hr = response.json()
            symbol_quote_volume_data = [{'symbol': entry['symbol'], 'quote_volume': entry['quoteVolume']}
                                        for entry in sorted(data_24hr, key=lambda x: float(x['quoteVolume']), reverse=True)]
            return symbol_quote_volume_data
        else:
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None


if __name__ == "__main__":
    # 初始更新一次
    update_symbol_quote_volume_data()

    def job():
        update_symbol_quote_volume_data()

    # 五分鐘更新一次
    scheduler = BackgroundScheduler()
    scheduler.add_job(job, 'interval', minutes=5)
    scheduler.start()

    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
