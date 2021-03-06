'''
Created on 2018年8月16日

@author: qiaoxiaofeng
'''
from blockuser.basequant import quantpolicy
import ccxt
from acom.utils.strutil import green, blue, red, dump
import asyncio
import uvloop
from blockdjcom.decorators import monit_time
from blockdjcom.basebusiness import wslog

class LimitBuy(quantpolicy):
    
    def __init__(self, exchange, symbol, accesskey, secretkey,\
                 max_buy_price, min_sell_price, base_volume, limit_price):
        super().__init__(exchange, symbol, accesskey, secretkey)
        self.max_buy_price = max_buy_price
        self.min_sell_price = min_sell_price
        self.base_volume = base_volume
        self.limit_price = limit_price
        self.instance = None
    
    def run(self):
        try:
            id = self.exchange
            # check if the exchange is supported by ccxt
            exchange_found = id in ccxt.exchanges
            if exchange_found:
                dump('Instantiating', green(id))
                exchange = getattr(ccxt, id)({
                    # 'proxy':'https://cors-anywhere.herokuapp.com/',
                    'apiKey': self.accesskey,
                    'secret': self.secretkey,
                    #'enableRateLimit': True,
                    })
                self.instance = exchange
                # load all markets from exchange
                markets = exchange.load_markets()
                # output all symbols
                #dump(green(id), 'has', len(exchange.symbols), 'symbols:', green(', '.join(exchange.symbols))) 
                # don't check balance for speed
                if self.limit_price > self.max_buy_price or self.limit_price < self.min_sell_price:
                    return
                else:
                    # begin duiqiao
                    results = self.limitbuy_async(self.limit_price)
                    return results
            else:
                dump('Exchange ' + (id) + ' not found')
                return 'Exchange ' + (id) + ' not found'
        except ccxt.DDoSProtection as e:
            print(type(e).__name__, e.args, 'DDoS Protection (ignoring)')
            return type(e).__name__ + e.args + 'DDoS Protection (ignoring)'
        except ccxt.RequestTimeout as e:
            print(type(e).__name__, e.args, 'Request Timeout (ignoring)')
            return type(e).__name__ + e.args + 'Request Timeout (ignoring)'
        except ccxt.ExchangeNotAvailable as e:
            print(type(e).__name__, e.args, 'Exchange Not Available due to downtime or maintenance (ignoring)')
            return type(e).__name__ + e.args + 'Exchange Not Available due to downtime or maintenance (ignoring)'
        except ccxt.AuthenticationError as e:
            print(type(e).__name__, e.args, 'Authentication Error (missing API keys, ignoring)')
            return type(e).__name__ + e.args + 'Authentication Error (missing API keys, ignoring)'
 
    async def create_order(self, price, side):
        try:
            if side == 'sell':
                response = self.instance.create_limit_sell_order(self.symbol, self.base_volume, price)
            elif side == 'buy':
                response = self.instance.create_limit_buy_order(self.symbol, self.base_volume, price)
        except Exception as e:
            print('Failed to create order with', self.instance.id, type(e).__name__, str(e))
            return 'Failed to create order with' + self.instance.id +  type(e).__name__ + str(e)
            response = None
        return response
 
    @monit_time
    def limitbuy_async(self, price):
        loop = uvloop.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(asyncio.gather(
            self.create_order(price, 'buy'),
            self.create_order(price, 'buy'),
            self.create_order(price, 'buy'),
            self.create_order(price, 'buy'),
            self.create_order(price, 'buy')
            ))     
        return results
    
    @monit_time
    def limitsell(self, price, currency):
        balances = self.instance.fetchBalance() 
        balances_item = balances['info']['data']['list']
        sell_amount = 0
        for item in  balances_item:
            if item['currency'].upper() == currency and item['type'] == 'trade':
                sell_amount = item['balance']
                break
        # sell the currency amount 
        if sell_amount == 0:
            return
        try:
            response = self.instance.create_limit_sell_order(self.symbol, sell_amount, price)
        except Exception as e:
            print('Failed to create order with', self.instance.id, type(e).__name__, str(e))
            return 'Failed to create order with' + self.instance.id +  type(e).__name__ + str(e)
    @monit_time
    def cancelorder(self):
        orders = self.instance.fetchOpenOrders(self.symbol)
        for order in orders:
            orderid = order['info']['id']
            self.instance.cancelOrder(orderid)
            