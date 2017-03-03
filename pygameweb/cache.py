from flask_caching import Cache

cache = Cache()


# Add some basic rate limiting.
# https://flask-limiter.readthedocs.io/en/stable/
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
limiter = Limiter(key_func=get_remote_address)
