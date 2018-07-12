from js9 import j


class Order(object):
    def __init__(self, order_type='sell'):
        self.type = order_type # order type (sell/buy)
        self.schema = j.data.schema.schema_from_url('threefoldtoken.order.%s' % self.type)
        self.orders = j.servers.gedis2.latest.context['%s_orders' % self.type]
        self.db_table = j.servers.gedis2.latest.db.tables['order%s' % self.type]
        self.matcher = j.servers.gedis2.latest.context['matcher']

    def add(self, wallet, order):
        """
        Add order

        :param order: Order
        :type order: !threefoldtoken.order.sell or !threefoldtoken.order.buy
        :param wallet: Cuurent wallet
        :type wallet: !threefoldtoken.wallet
        :return: Order ID
        :rtype: int
        """
        order.owner_email_addr = wallet.email
        order.wallet_addr = wallet.addr

        o = self.db_table.set(id=None, data=order.data)

        # Put order into memory cache
        self.orders[o.id] = o

        # if order id approved already, put it into matcher to be processed
        if o.approved:
            self.matcher.add_order(o)

        return o.id

    def update(self, wallet, order):
        """
        Update Sell order

        :param wallet: Cuurent wallet
        :param order: Order
        :type order: !threefoldtoken.order.sell or !threefoldtoken.order.buy
        :type wallet: !threefoldtoken.wallet
        """

        if type(order.id) != int:
            raise RuntimeError('An int (id) field is required')

        # not found
        if order.id not in self.orders:
            raise RuntimeError('not found')

        old_order = self.orders.get(order.id)

        # client tries to update an order that
        # assigned to a different wallet than client wallet
        if old_order.wallet_addr != wallet.addr:
            raise RuntimeError('Not authorized')

        # order is approved (being processed in matching process)
        # no further updates possible
        if old_order.approved:
            raise RuntimeError('Order is approved(being processed). No more updates are possible')

        order.owner_email_addr = wallet.email
        order.wallet_addr = wallet.addr

        # Persist to db
        # Only to keep track of history
        self.db_table.set(id=order.id, data=order.data)

        # update order in memory cache
        self.orders[order.id] = order

        # if order id approved already, put it into matcher to be processed
        if order.approved:
            self.matcher.add_order(order)

        return order.id

    def remove(self, wallet, order_id):
        """
        Remove Sell order

        :param wallet: Cuurent wallet
        :type wallet: !threefoldtoken.wallet
        :param order_id: order id
        :rtype order_id: int
        """

        order_id = int(order_id)

        # not found
        if order_id not in self.orders:
            raise RuntimeError('not found')

        order = self.orders.get(order_id)

        # client tries to update an order that
        # assigned to a different wallet than client wallet
        if order.wallet_addr != wallet.addr:
            raise RuntimeError('Not authorized')

        # order is approved (being processed in matching process)
        # no further updates possible
        if order.approved:
            raise RuntimeError('Order is approved(being processed). deletes are impossible')

        self.orders.pop(order_id)
        return order_id

    def list(self, wallet=None, sortby='id', desc=False, ddict_hr=False, **kwargs):
        """
        List / Filter Sell order in current user wallet
        If wallet is provided, get user orders only
        If wallet is None, retrieve all orders

        :param wallet: Cuurent wallet
        :type wallet: !threefoldtoken.wallet
        :param sortby: field to sort with
        :type sortby: str
        :param desc: Descending order
        :type desc: bool
        :param ddict_hr: return data as list of dicts
        :type ddict_hr: bool
        :param exclude_wallet_data: exclude wallet info
        :type exclude_wallet_data: bool

        :return: List of Sell orders
        :rtype: list
        """

        # we prepare a copy of orders
        # we don't return actual orders in memory to prevent
        # accident manipulation
        orders = []

        for k, v in self.orders.items():
            # get a copy of that object
            new = self.schema.get(capnpbin=v.data)
            new.id = v.id
            v = new

            # Filter only orders belonging to certain wallet if provided
            if wallet is not None and v.wallet_addr != wallet.addr:
                continue

            # filter only orders matching the passed kwargs filters (exact values)
            valid = True
            for field, value in kwargs.items():
                if hasattr(v, field) and getattr(v, field) != value:
                    valid = False
                    break

            if valid:
                if ddict_hr:
                    v = v.ddict_hr
                orders.append(v)

        if not sortby:
            sortby = 'id'

        def sort_func(order):
            if ddict_hr:
                return order.get(sortby)
            return getattr(order, sortby)

        orders.sort(key=sort_func, reverse=desc)

        return orders

    def get(self, wallet, order_id):
        """
          get a Sell order by ID

          :param wallet: Cuurent wallet
          :type wallet: !threefoldtoken.wallet
          :param order_id: order id
          :rtype order_id: int
        """
        order_id = int(order_id)

        # not found
        if order_id not in self.orders:
            raise RuntimeError('not found')

        order = self.orders.get(order_id)
        # client tries to update an order that
        # assigned to a different wallet than client wallet
        if order.wallet_addr != wallet.addr:
            raise RuntimeError('Not authorized')
        return order
