from js9 import j
from gevent.event import Event
import cryptocompare
from orderbook.lib.transaction import Transaction
import gevent

JSBASE = j.application.jsbase_get_class()
Numeric = j.data.types.numeric
Date = j.data.types.date


class Matcher(JSBASE,):
    """
    Matcher
    """
    def __init__(self):
        # Maintain a copy of approved sell & buy ordders
        # This version can be manipulated
        # at any instance of time it will contain the current state
        # of order book
        JSBASE.__init__(self)
        self.approved_sell_orders = []
        self.approved_buy_orders = []
        self.evt = Event()
        g = gevent.spawn(self.run)
        g.start()

    @property
    def trader(self):
        return j.servers.gedis.latest.context['trader']

    def add_order(self, order):
        """
        Append order
        :param order: order
        :type order: !threefoldtoken.buy or !threefoldtoken.sell
        """
        if order.schema.name == 'orderbuy':
            self.approved_buy_orders.append(order.ddict_hr)
        else:
            self.approved_sell_orders.append(order.ddict_hr)
        self.evt.set()
        gevent.sleep(0)
        self.evt.clear()

    def run(self):
        """ run the matcher whenever any order is added to the orderbookmm  
        this should be spawned by gevent
        
        """
        while(True):
            self.logger.info("Waiting for new orders to match")
            self.evt.wait()
            gevent.sleep(0)
            self.logger.info("Matching started")
            transactions = self.match(self.approved_sell_orders, self.approved_buy_orders)
            if transactions:
                self.trader.put(transactions)
            self.clean()
            self.visualize_lists(self.approved_sell_orders, self.approved_buy_orders)
            self.logger.info("Done matching")

    def match(self, sell_list, buy_list):
        """executes matching between list of sell orders and a list of buy orders
        will compare eache buy order againest all sell orders
        
        :param sell_list: list of sell orders
        :type sell_list: list
        :param buy_list: list of buy orders
        :type buy_list: list
        """
        transactions = []
        buy_list = sorted(buy_list, key=lambda order: order['id'], reverse=False)
        buy_list = sorted(buy_list,
                          key=lambda order: Numeric.bytes2cur(Numeric.str2bytes(order['price_max'])),
                          reverse=True)
        sell_list = sorted(sell_list, key=lambda order: order['id'], reverse=False)
        for buy_order in buy_list:
            if buy_order['amount'] == 0:
                continue
            fulfilled = False
            while not fulfilled:
                best_sell = None
                best_sell_index = None
                for index, sell_order in enumerate(sell_list):
                    if sell_order['amount'] == 0:
                        continue
                    if self.is_valid(sell_order, buy_order):
                        if best_sell == None:
                            best_sell = sell_order
                            best_sell_index = index
                        else:
                            best_sell_price = best_sell['price_min']
                            current_sell_price = sell_order['price_min']
                            if self.currencies_compare(best_sell_price, current_sell_price) == 1: # if the best sell price is bigger than the current sell price
                                best_sell = sell_order
                                best_sell_index = index
                if not best_sell:
                    break

                trade_amount = 0
                if best_sell['amount'] == buy_order['amount']:
                    trade_amount = best_sell['amount']
                    buy_order['amount'] = 0
                    sell_list[best_sell_index]['amount'] = 0
                    fulfilled = True
                elif best_sell['amount'] < buy_order['amount']:
                    trade_amount = best_sell['amount']
                    buy_order['amount'] -= best_sell['amount']
                    sell_list[best_sell_index]['amount'] = 0
                elif best_sell['amount'] > buy_order['amount']:
                    trade_amount = buy_order['amount']
                    sell_list[best_sell_index]['amount'] -= buy_order['amount']
                    buy_order['amount'] = 0
                    fulfilled = True

                transaction = Transaction.new(
                    best_sell['id'],
                    buy_order['id'],
                    trade_amount,
                    buy_order['currency_to_buy'],
                    self.price_get(sell_order,buy_order,trade_amount),
                    buy_order['wallet_addr'],
                    best_sell['wallet_addr'],
                    buy_order['owner_email_addr'],
                    best_sell['owner_email_addr'])
                transactions.append(transaction)
        
        print(transactions)
        return transactions

    def currencies_compare(self, currency1, currency2):
        """compares two string representations of currency
        if both parameters of the same currency it will directly compare values
        otherwise the second parameter will be be converted to the first parameter currency first
        Example:
        self.currencies_compare("10.0 EUR", "10.0 USD")
        
        :param currency1: string reprentation of currency1
        :type currency1: string
        :param currency2: string reprentation of currency1
        :type currency2: string

        :return 
        0 means equal
        1 greater than
        -1 less than
        """
        currency1_value ,currency1_currency = Numeric.getCur(currency1)
        currency2_value ,currency2_currency = Numeric.getCur(currency2)

        if currency1_currency != currency2_currency:
            currency2_value = self.currency_convert(currency2_currency, float(currency2_value), currency1_currency)
            currency2_currency = currency1_currency

        # its safe now to compare value
        if float(currency1_value) == float(currency2_value):
            return 0
        elif float(currency1_value) < float(currency2_value):
            return -1
        elif float(currency1_value) > float(currency2_value):
            return 1

    def currency_convert(self, currency, amount, target):
        """convert between two currencies
        
        :param currency: the currency to be converted
        :type currency: string
        :param amount: amount of currency to be converted
        :type amount: float
        :param target: currency to convert to
        :type target: float
        :return: value after conversion
        :rtype: float
        """
        price1 = j.clients.currencylayer.cur2usd[target]
        price2 = j.clients.currencylayer.cur2usd[currency]
        return (price1 / price2) * amount

    def price_get(self, sell_order, buy_order, amount):
        """Get the total price of a transactionm
        
        :param sell_order: the sell order
        :type sell_order: dict
        :param buy_order: the buy order
        :type buy_order: dict
        :param amount: the anount to be transfered
        :type amount: float
        :return: the transaction price
        :rtype: float
        """
        common_currency = [currency for currency in sell_order['currency_accept'] if currency in buy_order['currency_mine']][0]
        sell_value, sell_currency = Numeric.getCur(sell_order['price_min'])
        return amount * self.currency_convert(sell_currency.casefold(), float(sell_value), common_currency.casefold())

    def is_valid(self, sell_order, buy_order):
        """this method checks if the two orders can be matched or not according the following
        1- check expiration for both orders
        2- check if these orders have secrets, and validate these secrets
        3- check if these orders have the same currencies targeted
        4- check if the price_max for the buy order is greater than or equal price_min for sell order 
        
        :param sell_order: sell order
        :type sell_order: dict
        :param buy_order: buy order
        :type buy_order: dict
        """
        now = j.data.time.epoch
        if Date.fromString(sell_order['expiration']) < now or Date.fromString(buy_order['expiration']) < now:
            return False
        
        if len(sell_order['secret']) > 0 or len(buy_order['secret']) > 0:
            if not buy_order['secret'] in sell_order['secret']:
                return False

        interesection = set(sell_order['currency_accept']) & set(buy_order['currency_mine']) #if not none means that the buyer accepts one of the seller's currencies
        if sell_order['currency_to_sell'] != buy_order['currency_to_buy'] or not interesection:
            return False

        if self.currencies_compare(sell_order['price_min'], buy_order['price_max']) == 1:
            return False

        return True

    def clean(self):
        """deletes all expired orders and orders with 0 amount
        
        """
        now = j.data.time.epoch
        valid_buy_orders = []
        for order in self.approved_buy_orders:
            if Date.fromString(order['expiration']) > now and order['amount'] > 0:
                valid_buy_orders.append(order)
        self.approved_buy_orders = valid_buy_orders

        valid_sell_orders = []
        for order in self.approved_sell_orders:
            if Date.fromString(order['expiration']) > now and order['amount'] > 0:
                valid_sell_orders.append(order)
        self.approved_sell_orders = valid_sell_orders


    def visualize_lists(self, sell_orders, buy_orders):
        print("TYPE\t id\t AMOUNT\t PRICE")
        for sell_order in sell_orders:
            print("SELL\t {}\t {}\t {}".format(sell_order['id'], sell_order['amount'], sell_order['price_min']))
        for buy_order in buy_orders:
            print("BUY\t {}\t {}\t {}".format(buy_order['id'], buy_order['amount'], buy_order['price_max']))
