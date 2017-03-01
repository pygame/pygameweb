from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'simple'})


# Add some basic rate limiting.
# https://flask-limiter.readthedocs.io/en/stable/
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
limiter = Limiter(key_func=get_remote_address,
                  global_limits=["200 per day", "50 per hour"])
