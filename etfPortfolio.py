import pandas as pd 
import yfinance as yf

#rates = [4.0, 7.0, 10.0]
etfs = ['EFA', 'GSG','IEF', 'IJH', 'IJR', 'LQD', 'RWR', 'SPY' ,'VWO']
splv = yf.Ticker('SPLV').history(start='2015-11-26', end='2024-03-15')
splvFrame = pd.DataFrame(splv)
pspy = 0
qsplv = 0
payout = 0
quantity = 100
index = 0
export = open('results.csv', 'w')

def difference(prev, cur):
   difference = ((float(cur) - float(prev)) / prev) * 100
   return difference

def calculatePeriodReturn(etfFrame, loss, startIndex, endIndex, quantity):
    currentHigh = float(etfFrame.iloc[startIndex]['High'])
    for i in range(startIndex + 1, endIndex):
        percentDiff = difference(currentHigh, float(etfFrame.iloc[i]['High']))
        #set new high price if daily high goes above previous high
        if(percentDiff > 0):
            currentHigh = etfFrame.iloc[i]['High']
        #triggers for high price
        elif (percentDiff <= loss * -1):
            #payout of ETF and SPLV at end of period if TLS occurs
            payout = quantity * float(etfFrame.iloc[i]['Close'])
            #calculate number of shares of SPLV that can be purchased on the day the TLS triggers
            qsplv = int(payout / float(splvFrame.iloc[i]['Open']))
            payout = qsplv * (splvFrame.iloc[endIndex]['Close'])
            return payout
        #check the low price
        elif(difference(currentHigh, float(etfFrame.iloc[i]['Low'])) <= loss * -1):
            payout = quantity * float(etfFrame.iloc[i]['Close'])
            #calculate number of shares of SPLV that can be purchased on the day the TLS triggers
            qsplv = int(payout / float(splvFrame.iloc[i]['Open']))
            payout = qsplv * (splvFrame.iloc[endIndex]['Close'])
            return payout
        #check closing price
        elif (difference(currentHigh, float(etfFrame.iloc[i]['Close'])) <= -1 * loss):
            payout = quantity * float(etfFrame.iloc[i]['Close'])
            #calculate number of shares of SPLV that can be purchased on the day the TLS triggers
            qsplv = int(payout / float(splvFrame.iloc[i]['Open']))
            payout = qsplv * (splvFrame.iloc[endIndex]['Close'])
            return payout
    #record payout of ETF shares if TLS never triggers
    payout = quantity*etfFrame.iloc[endIndex]['Close']
    return payout
            
def calculateETFShares(dollars, index, etfFrame):
    price = float(etfFrame.iloc[index]['Open'])
    spyShares = dollars/price
    return int(spyShares)

def calculateStop():
    export.write("ETF" +str(",") + "Stoploss" + "\n")
    for etf in etfs:
        etfData = yf.Ticker(etf)
        etfHistory = etfData.history(start='2015-11-26', end='2024-03-15')
        etfFrame = pd.DataFrame(etfHistory)
        period = 4
        interval = int(len(etfFrame) / period)
        loss = 0
        bestReturn = 0
        bestLoss = 0
        quantity = 100
        returns = 0
        startIndex = 0
        while loss < 51.0:
            for i in range(1,period):
                returns = calculatePeriodReturn(etfFrame, loss, startIndex, interval * i, quantity) #returns from each period 
                quantity = calculateETFShares(returns, interval * i, etfFrame) # calculate new shares of ETF
                startIndex = startIndex + interval
            returns = round(calculatePeriodReturn(etfFrame, loss, (period - 1) * interval, len(etfFrame) -1, quantity),2)

            if returns > bestReturn:
                bestReturn = returns
                bestLoss = loss
            loss = loss + 1.0
            startIndex = 0
            returns = 0
            quantity = 100
        print(f"Best return for {etf} is a stop loss of {bestLoss}%")
        export.write(str(etf) + "," + str(bestLoss/100) + "\n")
        print("\n")
    export.close()

def main():
    calculateStop()

main()