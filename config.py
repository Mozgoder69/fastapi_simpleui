# config.py

# Import necessary libraries
from os import getenv
from secrets import token_hex


class Config:
    """Class to store configuration parameters."""

    def __init__(self, **kwargs):
        # Initialize configuration parameters from passed arguments
        self.__dict__.update(kwargs)


# Database superuser configuration
db_super = Config(uname="postgres")

# Public database access configuration
db_public = Config(
    uname=getenv(
        "db_uname", "customer"
    ),  # Username from environment or default "customer"
    pword=getenv(
        "db_pword", "customer"
    ),  # Password from environment or default "customer"
)

# General database connection parameters
db_params = Config(
    host=getenv("db_host", "localhost"),  # Database host
    port=int(getenv("db_port", "1618")),  # Database port
    base=getenv("db_base", "cleaners"),  # Database name
)

# Connection pool configuration
pool_size = Config(
    min_size=1,  # Minimum number of connections in pool
    max_size=15,  # Maximum number of connections in pool
)

# JWT signing configuration
jwt_sign = Config(
    alg="HS256",  # Algorithm for signing tokens
    key=token_hex(32),  # Randomly generated key for signing tokens
)

# Token lifetime configuration in seconds
jwt_exp = Config(
    at_exp=900,  # Access token expiration
    st_exp=9000,  # Session token expiration
    rt_exp=90000,  # Refresh token expiration
)
