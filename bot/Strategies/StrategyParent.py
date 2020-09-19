from bot.Indicators import AddIndicator
from abc import ABC, abstractmethod


class Strategy(ABC):
    # TODO look at incorporating exceptions for this class
    def __init__(self):
        self.price = None
        self.buy_price = None
        self.stop_price = None
        self.quantity = None
        self.current_price = None
        self.df = None
        self.indicators = None
    
    def set_up(self):
        self.current_price = self.df.iloc[-1]['close']
        self.choose_indicators()
        if self.indicators is not None:
            # Create all asked indicators
            for indicator in self.indicators:
                # Create a list of all arguments that are not the indicator name or column name
                exclude_keys = set(['indicator_name', 'col_name'])
                args = [indicator[k] for k in set(list(indicator.keys())) - exclude_keys]
                
                AddIndicator(self.df, indicator['indicator_name'], indicator['col_name'], *args)
    
    def look_for_buy(self, df):
        self.df = df
        self.set_up()
        i = len(self.df) - 1
        return self.check_buy_signal(i)
        
    def execute_buy(self):
        self.go_buy()
        # probably also want to move qty to here
        if self.buy_price is not None:
            return dict(price = self.buy_price)
        
    def look_for_sell(self, df):
        self.df = df
        self.set_up()
        i = len(self.df) - 1
        return self.check_sell_signal(i)
    
    def execute_sell(self):
        self.go_sell()
        # This one now only handles limit stop loss but ofc it can be made such that all orders can be handled.
        # Want to see what u guys think first before I work this out completely.
        if self.price is not None:
            order_type = self._determine_order_type(self.price)
            if order_type == 'MARKET_ORDER':
                pass
            if order_type == 'LIMIT_ORDER':
                pass
            if order_type == 'STOP_LOSS_LIMIT':
                return dict(price = self.price, stop_price = self.stop_price)
            
    def _determine_order_type(self, price):
        if self.current_price == price:
            return 'MARKET_ORDER'
        if self.current_price < price:
            return 'LIMIT_ORDER'
        if self.current_price > price:
            return 'STOP_LOSS_LIMIT'

    @abstractmethod
    def check_buy_signal(self, i):
        pass
    
    @abstractmethod
    def check_sell_signal(self, i):
        pass

    @abstractmethod
    def go_buy(self):
        pass

    @abstractmethod
    def go_sell(self):
        pass

    @abstractmethod
    def choose_indicators(self):
        pass
    