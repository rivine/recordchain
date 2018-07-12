from orderbook.lib.order import Order
from orderbook.lib.transaction import Transaction

from orderbook.lib.wallet import Wallet
from orderbook.lib.decorators import is_logged_in


class OrderBook(object):

    wallet = Wallet()

    _buy = None
    _sell = None
    _transactions = None

    @property
    @is_logged_in
    def buy(self):
        if not self._buy:
            self._buy = Order('buy')
        return self._buy

    @property
    @is_logged_in
    def sell(self):
        if not self._sell:
            self._sell = Order('sell')
        return self._sell

    @property
    @is_logged_in
    def transactions(self):
        if not self._transactions:
            self._transactions = Transaction()
        return self._transactions
