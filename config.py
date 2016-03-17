import os

class BaseConfig(object):
  DEBUG = False
  # generate your own SECRET_KEY:
  #   r = os.urandom(128)
  #   r.encode('base-64')
  SECRET_KEY = 'cMPGZGkobeee1xQoubwU++hMjysvFFqC/y9Ldrw8db+winm8Eh85rVoHBygbZ4YUW1htofRB2YOD\nIKdoIQ+NHwCGa6xdap5SXks0UMwA2+PmGWK0AOk1X5c1EvxAsQK+2R5q76WAR0YCf0cY5T5FOTTr\nQIQISY8ifxPL7JwU2a0=\n'
  DATABASE = 'cellipede.db'

class DevelopmentConfig(BaseConfig):
  DEBUG = True

class ProductionConfig(BaseConfig):
  DEBUG = True
