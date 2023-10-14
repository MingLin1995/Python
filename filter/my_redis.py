# my_redis.py
import redis  # pip install redis
import pickle

""" 建立Redis連接 """
redis_pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
redis_client = redis.StrictRedis(connection_pool=redis_pool)

""" 儲存標的、成交量"""


def save_data_to_redis(data):
    # 使用Redis的set方法將數據儲存到Redis中
    redis_client.set('symbol_quote_volume_data',
                     pickle.dumps(data), ex=60*5*2)  # 過期時間10分鐘(秒計算)


""" 載入標的、成交量"""


def load_data_from_redis():
    cached_data = redis_client.get('symbol_quote_volume_data')
    if cached_data:
        return pickle.loads(cached_data)
    else:
        return None


""" 時框、過期時間(分鐘) """
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

""" 儲存K線資料 """


def save_klines_data_to_redis(data, time_interval):
    expiration_time = time_intervals.get(time_interval)
    # 使用Redis的set方法將數據儲存到Redis中，根據時間間隔構建鍵名
    redis_client.set(f'kilne_data_{time_interval}',
                     pickle.dumps(data), ex=(expiration_time*60)*2)  # 過期時間動態調整(更新時間兩倍)


""" 載入K線資料 """


def load_klines_data_from_redis(time_interval):
    # 根據時間間隔構建鍵名，然後從Redis中加載數據
    key = f'kilne_data_{time_interval}'
    cached_data = redis_client.get(key)
    if cached_data:
        return pickle.loads(cached_data)
    else:
        return None
