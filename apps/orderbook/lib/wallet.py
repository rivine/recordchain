from js9 import j
from orderbook.lib.iyo import Iyo


class Wallet(object):

    def __init__(self):
        self._current = None

    def register(self, wallet):
        """
        Register new wallet
        :param wallet: wallet
        :type wallet: !threefoldtoken.wallet
        :return: !threefoldtoken.wallet
        """
        user = Iyo.get_user(wallet.jwt)
        wallet.username = user['username']
        wallet.email = user['email']

        # Set current wallet
        self._current = wallet

        if wallet.addr in j.servers.gedis.latest.context['wallets']:
            if j.servers.gedis.latest.context['wallets'][wallet.addr].email != wallet.email:
                raise RuntimeError('Wallet already registered with a different user')

        # Add wallet to list of all wallets in system
        j.servers.gedis.latest.context['wallets'][wallet.addr] = wallet

        return wallet

    def update(self):
        pass

    @property
    def current(self):
        """
        Get Current user wallet (if already registered)
        :return: Current Wallet
        :rtype: !threefoldtoken.wallet
        """
        return self._current

    def get(self, addr):
        """
        Get a wallet giving
        :param addr:
        :return:
        """
        return j.servers.gedis.latest.context['wallets'].get(addr)

    def remove(self, addr):
        """
        Remove a wallet
        :param addr: Wallet addr
        :rtype addr: str
        """
        if addr in j.servers.gedis.latest.context['wallets']:
            return j.servers.gedis.latest.context['wallets'].pop(addr)

    def list(self):
        """
        List wallets
        :return: List of wallets
        :rtype: list
        """
        return j.servers.gedis.latest.context['wallets']
