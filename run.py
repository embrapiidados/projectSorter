from app import create_app
from config import Config
import argparse

app = create_app()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the Flask application')
    parser.add_argument('--port', type=int, default=5001, help='Port to run the server on')
    args = parser.parse_args()
    
    app.run(debug=True, port=args.port)
