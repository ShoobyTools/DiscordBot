class Cost:
    def __init__(self, limit, utilization, gas, price, num):
        self.limit = limit
        self.utilization = utilization / 100
        self.gas = gas
        self.price = price
        self.num = num
        self.utilization_total = (self.limit * self.utilization * self.gas * 0.000000001 * self.num) + (self.price * self.num)
        self.max_total = (self.limit * self.gas * 0.000000001 * self.num) + (self.price * self.num)
        self.utilization_average = round(self.utilization_total / self.num, 7)
        self.max_average = round(self.max_total / self.num, 7)
        self.utilization_total = round(self.utilization_total, 7)
        self.max_total = round(self.max_total, 7)

gas_prices = [100, 200, 300 , 400, 500, 600, 700, 800, 900, 1000, 1500, 2000, 3000]

# gas cost - total cost - average
def calculate(limit, utilization, price_per, num, custom):
    costs = []
    if custom == -1:
        for i in gas_prices:
            costs.append(Cost(limit, utilization, i, price_per, num))
    else:
        costs.append(Cost(limit, utilization, custom, price_per, num))
    
    return costs