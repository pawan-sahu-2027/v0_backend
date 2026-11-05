# import gevent
# from gevent import monkey
# monkey.patch_all()

# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS
# from config import Config
# from models import db
# from routes import initialize_routes
# from socket_instance import init_socketio
# import os

# app = Flask(__name__)
# app.config.from_object(Config)

# CORS(app, resources={
#     r"/*": {
#         "origins": "*",
#         "allow_headers": "*",
#         "expose_headers": "*",
#         "supports_credentials": True,
#         "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"]
#     }
# })

# db.init_app(app)

# with app.app_context():
#     # Create all tables if they don't exist
#     # Note: This only creates tables, it doesn't modify existing tables
#     # For adding columns to existing tables, use migration scripts
#     db.create_all()

# # Initialize routes and SocketIO
# initialize_routes(app)
# socketio = init_socketio(app)

# if __name__ == '__main__':
#     try:
#         print("Starting server with eventlet mode...")
#         socketio.run(
#             app,
#             host='0.0.0.0',
#             port=5001,
#             debug=False,
#             use_reloader=True,
#             log_output=False,
#             allow_unsafe_werkzeug=True
#         )
#     except KeyboardInterrupt:
#         print("\nShutting down gracefully...")
#     except Exception as e:
#         print(f"\nError starting server: {str(e)}")
import gevent
from gevent import monkey
monkey.patch_all()

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import Config
from models import db
from routes import initialize_routes
from socket_instance import init_socketio
import os

app = Flask(__name__)
app.config.from_object(Config)

CORS(app, resources={
    r"/*": {
        "origins": "*",
        "allow_headers": "*",
        "expose_headers": "*",
        "supports_credentials": True,
        "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"]
    }
})

db.init_app(app)

with app.app_context():
    db.create_all()

# Initialize routes and SocketIO
initialize_routes(app)
socketio = init_socketio(app)

if __name__ == '__main__':
    try:
        print("Starting server with gevent mode...")
        socketio.run(
            app,
            host='0.0.0.0',
            port=5001,
            debug=False,
            use_reloader=False  # Recommended to avoid reloader thread monkey-patch warnings
        )
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"\nError starting server: {str(e)}")