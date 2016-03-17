from app import flask_app

# this is used in production by:
#   gunicorn -b 127.0.0.1:5000 run:flask_app

if __name__ == '__main__':
  flask_app.run()
