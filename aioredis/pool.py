import asyncio

from .commands import Redis


@asyncio.coroutine
def create_pool(address, db=None, password=None, *,
                minsize=10, maxsize=10, commands_factory=Redis, loop=None):
    """Creates Redis Pool.
    """

    pool = RedisPool(address, db, password,
                     minsize=minsize, maxsize=maxsize,
                     commands_factory=commands_factory,
                     loop=loop)
    yield from pool._feel_free()
    return pool


class RedisPool:
    """Redis pool.

    """

    def __init__(self, address, db=None, password=None,
                 *, minsize, maxsize, commands_factory, loop=None):
        if loop is None:
            loop = asyncio.get_event_loop()
        self._address = address
        self._db = db
        self._password = password
        self._minsize = minsize
        self._loop = loop
        self._pool = asyncio.Queue(maxsize, loop=loop)
        self._used = set()

    @property
    def minsize(self):
        """Minimum pool size.
        """
        return self._minsize

    @property
    def maxsize(self):
        """Maximum pool size.
        """
        return self._pool.maxsize

    @property
    def size(self):
        """Current pool size.
        """
        return self.freesize + len(self._used)

    @property
    def freesize(self):
        """Current number of free connections.
        """
        return self._pool.qsize()

    def clear(self):
        """Clear pool connections.

        Close and remove all free and used connections.
        """
        pass

    @asyncio.coroutine
    def acquire(self):
        pass
        # TODO: get free connection (or create one)
        # mark as used;
        # return it

    def release(self, conn):
        pass

    def _fill_free(self):
        pass

    def __enter__(self):
        raise RuntimeError(
            "'yield from' should be used as a context manager expression")

    def __exit__(self, *args):
        pass    # pragma: nocover

    def __iter__(self):
        conn = yield from self.acquire()
        return _ConnectionContextManager(self, conn)


class _ConnectionContextManager:

    __slots__ = ('_pool', '_conn')

    def __init__(self, pool, conn):
        self._pool = pool
        self._conn = conn

    def __enter__(self):
        return self._conn

    def __exit__(self, exc_type, exc_value, tb):
        try:
            self._pool.release(self._conn)
        finally:
            self._pool = None
            self._conn = None
