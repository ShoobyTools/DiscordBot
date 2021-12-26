class Cost:
    def __init__(self, limit, gas, price, num):
        self.limit = limit
        self.gas = gas
        self.price = price
        self.num = num
        self.total = (self.limit * self.gas * 0.000000001 * self.num) + (self.price * self.num)
        self.average = round(self.total / self.num, 7)
        self.total = round(self.total, 7)

gas_prices = [100, 200, 300 , 400, 500, 600, 700, 800, 900, 1000, 1500, 2000, 3000]

# gas cost - total cost - average
def calculate(limit, price_per, num, custom):
    costs = []
    if custom == -1:
        for i in gas_prices:
            costs.append(Cost(limit, i, price_per, num))
    else:
        costs.append(Cost(limit, custom, price_per, num))
    
    return costs