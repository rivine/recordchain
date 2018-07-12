def is_logged_in(f):
    """
    Check if user has already registered a wallet using valid JWT
    """
    def inner(self, *args, **kwargs):
        if not self.wallet.current:
            raise RuntimeError('Not-Authorized. Please login first')
        return f(self, *args, **kwargs)
    return inner
