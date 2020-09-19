from bot.Strategies.StrategyParent import Strategy

class strategy1(Strategy):
    
    def choose_indicators(self):
        self.indicators = dict(indicator_name  = 'sma', col_name = 'sma_fast', period = 5), dict(indicator_name = 'sma', col_name = 'sma_slow', period = 25)
        
    def check_buy_signal(self, i):
        
        df = self.df
        
        if i > 0 and df.sma_fast[i] >= df.sma_slow[i] and df.sma_fast[i-1] < df.sma_slow[i-1]:
            return True
        
        return False
        
    def go_buy(self):
        self.buy_price = 0.98 * self.current_price
    
    def check_sell_signal(self, i):
        # Try sell immediately
        return True
    
    def go_sell(self):
        self.price = 0.96 * self.current_price
        self.stop_price = 0.98 * self.current_price
    
    def check_update_open_position(self, i):
        # always update open position
        return True
    
    def update_open_position(self):
        # buy order maybe be open for max 2 hours in ms
        self.open_buy_order_time_out = 2 * 60 * 60 * 1000
        
        self.price = 0.96 * self.current_price
        self.stop_price = 0.98 * self.current_price