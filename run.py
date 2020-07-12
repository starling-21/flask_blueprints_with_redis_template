from counter_app import create_app
import os


if __name__ == "__main__":
    print("STARTING RUN.py")
    app = create_app()
    app.run(host='127.0.0.1', port=5000, debug=True)    