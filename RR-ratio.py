#風報比計算
Stop_Gain=float(input("停利點：")) 
Entry_price=float(input("進場價：")) 
Stop_Loss=float(input("停損點："))
Rate_of_risk_return=(Stop_Gain-Entry_price)/(Entry_price-Stop_Loss)
print("風報比：",Rate_of_risk_return)