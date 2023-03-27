#均價計算
Contract_Price=float(input("目前倉位價格:")) 
Contract_USDT=float(input("目前倉位數量:")) 
Plus_Price=float(input("加碼價格:")) 
Plus_USDT=float(input("加碼數量:")) 
AVG_Price=(Contract_Price*Contract_USDT)/(Contract_USDT+Plus_USDT)+(Plus_Price*Plus_USDT)/(Contract_USDT+Plus_USDT)
AVG_USDT=Contract_USDT+Plus_USDT
print("平均價格：",AVG_Price)
print("平均數量：",AVG_USDT)

#加碼數量計算
Contract_Price=float(input("目前倉位價格:")) 
Contract_USDT=float(input("目前倉位數量:")) 
Plus_Price=float(input("加碼價格:")) 
AVG_Price=float(input("期望的平均價格:")) 
Plus_USDT=(AVG_Price*Contract_USDT-Contract_Price*Contract_USDT)/(Plus_Price-AVG_Price)
print("應加碼的數量：",Plus_USDT)

#加密貨幣、台股、美股，計算邏輯都一樣，只要保持單位一致性及可