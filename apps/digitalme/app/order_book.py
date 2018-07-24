from js9 import j

from orderbook.lib.orderbook import OrderBook
from orderbook.lib.matcher import Matcher
from orderbook.lib.trader import Trader

JSBASE = j.application.jsbase_get_class()


class order_book(JSBASE):
    """
    This class functions are actually registered in

    """
    def __init__(self):
        JSBASE.__init__(self)

        if not hasattr(j.servers.gedis.latest, 'context'):
            j.servers.gedis.latest.context = {
                'wallets': {},
                'sell_orders':{},
                'buy_orders': {},
                'transactions': [],
                'matcher': Matcher(),
                'trader': Trader()
            }

        self.orderbook = OrderBook()

    def login(self, wallet, schema_out):
        """
        ```in
        !threefoldtoken.wallet
        ```

        ```out
        !threefoldtoken.wallet
        ```

        Verifies JWT and registers user wallet!

        :param jwt: JWT from Itsyouonline
        :param wallet_addr: Wallet address
        :param wallet_ipaddr: Wallet Ip address
        :param schema_out: !threefoldtoken.wallet
        :return: Wallet
        :rtype: !threefoldtoken.wallet
        """
        w = schema_out.new()
        w.ipaddr = wallet.ipaddr
        w.addr = wallet.addr
        w.jwt = wallet.jwt
        return self.orderbook.wallet.register(w)

    def add_sell_order(self,order):
        """
        ```in
        !threefoldtoken.order.sell
        ```

        Add a selling order

        :param order: Selling Order
        :type order: !threefoldtoken.order.sell
        :return: Order ID
        :rtype: int
        """

        return self.orderbook.sell.add(self.orderbook.wallet.current, order)

    def add_buy_order(self,order):
        """
        ```in
        !threefoldtoken.order.buy
        ```

        Add a buying order

        :param order: Buying Order
        :type order: !threefoldtoken.order.buy
        :return: Order ID
        :rtype: int
        """
        return self.orderbook.buy.add(self.orderbook.wallet.current, order)

    def update_sell_order(self, order):
        """"
        ```in
        !threefoldtoken.order.sell
        ```

        update a selling order

        :param order: Selling Order
        :type order: !threefoldtoken.order.sell
        :return: Order ID
        :rtype: int
        """
        return self.orderbook.sell.update(self.orderbook.wallet.current, order)

    def update_buy_order(self, order):
        """
        ```in
        !threefoldtoken.order.buy
        ```

        update a buying order

        :param order: Buying Order
        :type order: !threefoldtoken.order.buy
        :return: Order ID
        :rtype: int
        """
        return self.orderbook.buy.update(self.orderbook.wallet.current, order)

    def remove_sell_order(self, order_id):
        """
        Remove a selling order

        :param order_id: Selling order id
        :rtype order_id: int
        :return: Order ID
        :rtype int
        """
        return self.orderbook.sell.remove(self.orderbook.wallet.current, order_id)

    def remove_buy_order(self, order_id):
        """
        Remove a buying order

        :param order_id: Buying order id
        :rtype order_id: int
        :return: Order ID
        :rtype int
        """
        return self.orderbook.buy.remove(self.orderbook.wallet.current, order_id)

    def get_sell_order(self, order_id, schema_out):
        """
        ```out
        !threefoldtoken.order.sell
        ```

        Get a selling order

        :param order_id: Selling order id
        :type order_id: int
        :param schema_out: Order
        :type schema_out: !threefoldtoken.order.sell
        :return: order
        :rtype !threefoldtoken.order.sell
        """
        return self.orderbook.sell.get(self.orderbook.wallet.current, order_id)

    def get_buy_order(self, order_id, schema_out):
        """
        ```out
        !threefoldtoken.order.buy
        ```

        Get a buying order

        :param order_id: Buying order id
        :type order_id: int
        :param schema_out: Order
        :type schema_out: !threefoldtoken.order.sell
        :return: order
        :rtype !threefoldtoken.order.buy
        """
        return self.orderbook.buy.get(self.orderbook.wallet.current, order_id)

    def list_my_sell_orders(self, sortby, desc, total_items_in_page, page_number, schema_out):
        """
        ```in
            sortby = id (S) # Field name to sort with
            desc = (B) # Descending order
            total_items_in_page = 20 (I)
            page_number = 1 (I)
        ```
        ```out
            orders = (LO) !threefoldtoken.order.sell
        ```

        List Selling orders for current client only
        :return: list of selling orders
        :rtype: list
        """
        out = schema_out.new()

        for order in self.orderbook.sell.list(self.orderbook.wallet.current, sortby=sortby, desc=desc, total_items_in_page=total_items_in_page, page_number=page_number):
            out.orders.append(order)
        return out

    def list_my_buy_orders(self, sortby, desc, total_items_in_page, page_number, schema_out):
        """
        ```in
            sortby = id (S) # Field name to sort with
            desc = (B) # Descending order
            total_items_in_page = 20 (I)
            page_number = 1 (I)
        ```
        ```out
            orders = (LO) !threefoldtoken.order.buy
        ```

        List Buy orders for current client only
        :return: list of buying orders
        :rtype: list
        """
        out = schema_out.new()
        for order in self.orderbook.buy.list(self.orderbook.wallet.current, sortby=sortby, desc=desc, total_items_in_page=total_items_in_page, page_number=page_number):
            out.orders.append(order)
        return out

    def list_all_sell_orders(self, sortby, desc, total_items_in_page, page_number, schema_out):
        """
        ```in
            sortby = id (S) # Field name to sort with
            desc = (B) # Descending order
            total_items_in_page = 20 (I)
            page_number = 1 (I)
        ```
        ```out
            orders = (LO) !threefoldtoken.order.sell
        ```

        List Selling orders
        :return: list of selling orders
        :rtype: list
        """
        out = schema_out.new()

        for order in self.orderbook.sell.list(None, sortby=sortby, desc=desc, total_items_in_page=total_items_in_page, page_number=page_number):
            order.owner_email_addr = ''
            order.wallet_addr = ''
            out.orders.append(order)
        return out

    def list_all_buy_orders(self, sortby, desc, total_items_in_page, page_number, schema_out):
        """
        ```in
            sortby = id (S) # Field name to sort with
            desc = (B) # Descending order
            total_items_in_page = 20 (I)
            page_number = 1 (I)
        ```
        ```out
            orders = (LO) !threefoldtoken.order.buy
        ```

        List Buy orders
        :return: list of buying orders
        :rtype: list
        """
        out = schema_out.new()

        for order in self.orderbook.buy.list(None, sortby=sortby, desc=desc, total_items_in_page=total_items_in_page, page_number=page_number):
            order.owner_email_addr = ''
            order.wallet_addr = ''
            out.orders.append(order)
        return out

    def list_all_transactions(self, state, total_items_in_page, page_number, schema_out):
        """
        ```in
            state = (S)
            total_items_in_page = 20 (I)
            page_number = 1 (I)
        ```
        ```out
            transactions = (LO) !threefoldtoken.transaction
        ```

        list/filter all transactions

        :param state: transaction state i.e : new, pending, success, failure
        :rtype: string
        """
        out = schema_out.new()

        for transaction in self.orderbook.transactions.list(wallet=None, state=state, total_items_in_page=total_items_in_page, page_number=page_number):
            transaction.buyer_email_addr = ''
            transaction.seller_email_addr = ''
            out.transactions.append(transaction)
        return out

    def list_my_transactions(self, state, total_items_in_page, page_number, schema_out):
        """
        ```in
            state = (S)
            total_items_in_page = 20 (I)
            page_number = 1 (I)
        ```
        ```out
            transactions = (LO) !threefoldtoken.transaction
        ```

        list/filter all transactions for current client only

        :param state: transaction state i.e : new, pending, success, failure
        :rtype: string
        """
        out = schema_out.new()

        for transaction in self.orderbook.transactions.list(wallet=self.orderbook.wallet.current, state=state, total_items_in_page=total_items_in_page, page_number=page_number):
            out.transactions.append(transaction)
        return out
