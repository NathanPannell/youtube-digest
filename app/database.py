import os
from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["PSYCOPG_URL"]


@contextmanager
def get_connection():
    with psycopg.connect(
        DATABASE_URL,
        row_factory=dict_row,
    ) as connection:
        yield connection
