from flask import *
import concurrent.futures
# import time
from MA import process_interval
from my_redis import load_data_from_redis


app = Flask(__name__)


@app.route('/add_intervals', methods=['POST'])
def add_intervals_route():
    intervals = request.json
    # start_time = time.time()
    results = main(intervals)
    # end_time = time.time()
    # execution_time = end_time - start_time
    # print(f"執行時間：{execution_time} 秒")
    return jsonify({"message": results})


@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")


def main(intervals):

    # 多線程處理
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(process_interval, intervals))

    # 整理不同時間間隔篩所選出的標的
    results_dict = {}
    for result in results:
        if result is not None:
            time_interval, ma_results = result
            results_dict[time_interval] = ma_results
    # print(results_dict["15m"])

    # 取出所有時框的標的
    common_symbols = set.intersection(
        *(set(symbols) for symbols in results_dict.values()))
    common_symbols_list = list(common_symbols)

    # 取得標的、成交量資訊
    data = load_data_from_redis()
    # 儲存標的、成交量資訊
    matched_data = []

    for symbol in common_symbols_list:
        for entry in data:
            if entry['symbol'] == symbol:
                target_quote_volume = float(entry['quote_volume'])
                break
        matched_data.append({
            "標的": symbol,
            "成交量": target_quote_volume
        })

    # print(matched_data)
    # print(len(matched_data), "筆資料")
    return matched_data


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
