from js9 import j


class Transaction:
    def __init__(self):
        self.schema = j.data.schema.schema_from_url('threefoldtoken.transaction')
        self.trader = j.servers.gedis2.latest.context['trader']
        self.transactions = j.servers.gedis2.latest.context['transactions']
        self.db_table = j.servers.gedis2.latest.db.tables['transaction']

    def list(self, wallet=None, **kwargs):
        """
        List / Filter transactions

        if wallet is None, list/filtetr all transactions
        otherwise do it for transactions that current client is part of oly

        Filtration is done according to kwargs values
        for example ou can ask for state='pending' only to filter
        all pending transactions

        :param wallet: Cuurent wallet
        :type wallet: !threefoldtoken.wallet
        :kwargs: kwargs
        :type kwargs: dict
        :return list og transactions
        :rtype: list
        """
        # pop state if empty
        # to later match against all states
        if kwargs.get('state'):
            if kwargs['state'] == '':
                kwargs.pop('state')

            if kwargs['state'] not in ['new', 'pending', 'success', 'failure']:
                return []

        transactions = []
        for transaction in self.transactions:

            # get a copy of that object because we don't return references to
            # actual objects to prevent changing them
            v = self.schema.get(data=transaction)

            # Filter only transactions belonging to certain wallet if provided
            if wallet is not None and wallet.addr not in [v.buyer_wallet_addr, v.seller_wallet_addr]:
                continue

            for field, value in kwargs.items():
                if  getattr(v, field, None) != value:
                    break
            else:
                transactions.append(transaction)
        return transactions

    @classmethod
    def new(cls, sell_order_id, buy_order_id, amount, currency, price, buyer_wallet_addr, seller_wallet_addr, buyer_email_addr, seller_email_addr, state='new'):
        """
        Return new Transaction object
        :param sell_order_id: Sell order id
        :param buy order id
        :param amount: amount
        :type amount: float
        :param currency: currency
        :param price: Price
        :param buyer_wallet_addr: Buyer wallet address
        :param seller_wallet_addr: Seller walley address
        :param buyer_email_addr: Buyer email address
        :param seller_email_addr: Seller email address
        :param state: State # new, pending, success, failure
        :rtype state: string
        :return: new Transaction
        :rtype: !threefoldtoken.transaction
        """

        transaction = j.data.schema.schema_from_url('threefoldtoken.transaction').new()
        transaction.sell_order_id = sell_order_id
        transaction.buy_order_id = buy_order_id
        transaction.amount_bought = amount
        transaction.currency = currency
        transaction.total_price = price
        transaction.buyer_wallet_addr = buyer_wallet_addr
        transaction.seller_wallet_addr = seller_wallet_addr
        transaction.seller_email_addr = seller_email_addr
        transaction.buyer_email_addr = buyer_email_addr
        transaction.state = state

        
        db_table = j.servers.gedis2.latest.db.tables['transaction']
        

        transaction = db_table.set(id=None, data=transaction.data)

        return transaction
