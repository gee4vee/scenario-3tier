import logging
import psycopg2

# Globals
POSTGRESQL_TABLE = "count"
conn = None

def postgresql_table_create():
  """Validate or create a new table with one row"""
  table_exists = True
  with conn:
    with conn.cursor() as cur:
      try:
        cur.execute(f"SELECT * FROM {POSTGRESQL_TABLE};")
      except psycopg2.errors.UndefinedTable as eee:
        table_exists = False

  if not table_exists:
    with conn:
      with conn.cursor() as cur:
        try:
          sql = f"CREATE TABLE {POSTGRESQL_TABLE} (id INTEGER PRIMARY KEY, count INTEGER);"
          cur.execute(sql)
        except Exception as e:
          print(e)
          raise
  
  with conn:
    with conn.cursor() as cur:
      delete_table = False
      cur.execute(f"SELECT * from {POSTGRESQL_TABLE};")
      initial_rowcount = cur.rowcount
      if initial_rowcount == 1:
        row = cur.fetchone()
        logging.info(f"initial table contents {row}")
        if row[0] != 0:
          logging.info(f"expecting id to be 0, will delete table contents")
          delete_table = True
      if initial_rowcount > 1:
        logging.warning(f"expected 1 row in table got {cur.rowcount}, will delete table")
        delete_table = True
      if delete_table:
        cur.execute(f"DELETE FROM {POSTGRESQL_TABLE};")
      if delete_table or initial_rowcount == 0:
        cur.execute(f"INSERT INTO {POSTGRESQL_TABLE} (id, count) VALUES (%s, %s)", (0, 0))


def postgresql_increment():
  """Return the dict {count: num} where num is the number of times this function has been called update the table with the new count"""
  ret = dict(count=-1)
  with conn:
    with conn.cursor() as cur:
      cur.execute(f"SELECT * FROM {POSTGRESQL_TABLE};")
      assert cur.rowcount == 1
      row = cur.fetchone()
      assert row[0] == 0
      count = row[1] + 1
      cur.execute(f"UPDATE {POSTGRESQL_TABLE} SET count=(%s) WHERE id = (%s)", (count, 0))
      ret = dict(count=count)
  return ret


def initialize_postgresql(cache):
  """Initialize the conn global variable.  Create the table for the count"""
  global conn
  try:
    logging.info("postgresql connect")
    conn = psycopg2.connect(
      host=cache.postgresql_host,
      port=cache.postgresql_port,
      user=cache.postgresql_user,
      password=cache.postgresql_password,
      sslmode="verify-full", # not parsing queruyoptions = "?sslmode=verify-full"
      sslrootcert=cache.postgresql_certificate_file,
      database="ibmclouddb" # fixed
      )
  except Exception as e: 
    raise
  postgresql_table_create()

def teststuff():
  logging.info(f"server_version: {conn.server_version}")
  for parameter in ("server_version", "server_encoding", "client_encoding", "is_superuser", "session_authorization", "DateStyle", "TimeZone", "integer_datetimes"):
    logging.info(f"connection parameter {parameter}: {conn.get_parameter_status(parameter)}")
  # verify databases can be read
  with conn:
    with conn.cursor() as cur:
      logging.info(f"cursor scrollable: {cur.scrollable}")

    logging.info("postgresql read databases")
    with conn.cursor() as cur:
      cur.execute("""SELECT datname from pg_database""")
      logging.info(f"cursor description: {cur.description}")
      rows = cur.fetchall()
      for row in rows:
        logging.info(f"row {row[0]}")
    with conn.cursor() as cur:
      cur.execute("""SELECT datname from pg_database""")
      for row in cur:
        logging.info(f"row {row[0]}")



def get_increment_postgresql(cache):
  """return a dictionary for the count"""
  if conn == None:
    initialize_postgresql(cache)
  return postgresql_increment()