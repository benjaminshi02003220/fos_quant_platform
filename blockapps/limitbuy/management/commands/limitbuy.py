from django.core.management.base import BaseCommand
import time
from limitbuy.business import LimitBuy
import logging
from django.utils import timezone

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--ex', dest='exchange', required=True, \
                help='exchange')
        parser.add_argument('--pub', dest='publickey', required=True, \
                help='publick key')
        parser.add_argument('--pri', dest='privatekey', required=True, \
                help='private key')
        parser.add_argument('--symbol', dest='symbol', required=True, \
                help='trade symbol')
        parser.add_argument('--max', type=float, dest='max_buy_price', required=True, \
                help='max buy price')
        parser.add_argument('--min', type=float, dest='min_sell_price', required=True, \
                help='min sell price')
        parser.add_argument('--v', type=float, dest='base_volume', required=True, \
                help='basevolume to use')
        parser.add_argument('--p', type=float, dest='limit_price', required=True, \
                help='limit price to use')

    def handle(self, *args, **options):
        exchange = options['exchange']
        symbol = options['symbol']
        publickey = options['publickey']
        privatekey = options['privatekey']
        base_volume = options['base_volume']
        max_buy_price = options['max_buy_price']
        min_sell_price = options['min_sell_price']
        limit_price = options['limit_price']
        start_time = 1557406800000
        while True:
            nowtime = time.time()
            if int(nowtime*1000) > start_time - 1000:
                break
            time.sleep(0.05)
        while True:
            lasttime = time.time()
            if int(lasttime) > int(nowtime) + 3: 
                break
            policy = LimitBuy(exchange, symbol, publickey, privatekey, max_buy_price, min_sell_price, base_volume, limit_price)
            policy.run()
        currency = symbol.split('/')[0] 
        sell_price = limit_price * 3
        policy.cancelorder()
        policy.limitsell(sell_price, currency)
        time.sleep(2)
        sell_price = limit_price * 2
        policy.cancelorder()
        policy.limitsell(sell_price, currency)
        