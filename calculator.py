
# #開倉建議計算
# TA=float(input("總資金:")) 
# Stop_Loss=float(input("停損比率(百分比):"))/100
# Stop_Loss_Amount=TA*Stop_Loss 
# LS=input("做多輸入L，做空輸入S:")
# if LS=="L" :
#     Long_in=float(input("做多進場價格:"))
#     Long_out=float(input("做多停損價格:"))
#     Long_Loss_Point=Long_in-Long_out
#     Long_Open_U=Stop_Loss_Amount/Long_Loss_Point*Long_in
#     Long_Open_Unit=Long_Open_U/Long_in
#     print("建議開倉大小（U）:",Long_Open_U,"\n建議開倉大小（顆數）",Long_Open_Unit)
# elif LS=="S" :
#     Short_in=float(input("做空進場價格:"))
#     Short_out=float(input("做空停損價格:"))
#     Short_Loss_Point=Short_out-Short_in
#     Short_Open_U=Stop_Loss_Amount/Short_Loss_Point*Short_in
#     Short_Open_Unit=Short_Open_U/Short_in
#     print("建議倉大小（U）:",Short_Open_U,"\n建議開倉大小（顆數）",Short_Open_Unit)

# #進場點計算
# Stop_Gain=float(input("停利點：")) 
# Stop_Loss=float(input("停損點："))
# Rate_of_risk_return_2=(Stop_Gain-Stop_Loss)/3+Stop_Loss
# Rate_of_risk_return_2_5=(Stop_Gain-Stop_Loss)/3.5+Stop_Loss
# Rate_of_risk_return_3=(Stop_Gain-Stop_Loss)/4+Stop_Loss
# print("風報比2的進場點：",Rate_of_risk_return_2)
# print("風報比2.5的進場點：",Rate_of_risk_return_2_5)
# print("風報比3的進場點：",Rate_of_risk_return_3)

# #風報比計算
# Stop_Gain=float(input("停利點：")) 
# Entry_price=float(input("進場價：")) 
# Stop_Loss=float(input("停損點："))
# Rate_of_risk_return=(Stop_Gain-Entry_price)/(Entry_price-Stop_Loss)
# print("風報比：",Rate_of_risk_return)

# #均價計算(U)
# Contract_Price=float(input("目前倉位價格:")) 
# Contract_USDT=float(input("目前倉位數量（USDT）:")) 
# Plus_Price=float(input("加碼價格:")) 
# Plus_USDT=float(input("加碼數量（USDT）:")) 
# AVG_Price=(Contract_Price*Contract_USDT)/(Contract_USDT+Plus_USDT)+(Plus_Price*Plus_USDT)/(Contract_USDT+Plus_USDT)
# AVG_USDT=Contract_USDT+Plus_USDT
# print("平均價格：",AVG_Price)
# print("平均數量（USDT）：",AVG_USDT)

# #加碼數量（USDT）計算
# Contract_Price=float(input("目前倉位價格:")) 
# Contract_USDT=float(input("目前倉位數量（USDT）:")) 
# Plus_Price=float(input("加碼價格:")) 
# AVG_Price=float(input("期望的平均價格:")) 
# Plus_USDT=(AVG_Price*Contract_USDT-Contract_Price*Contract_USDT)/(Plus_Price-AVG_Price)
# print("應加碼的數量（USDT）：",Plus_USDT)

    

    
    
    
    
    
