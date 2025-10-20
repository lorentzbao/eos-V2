import hydra
from omegaconf import DictConfig
from app import create_app
import sys

@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg: DictConfig) -> None:
    app = create_app(cfg)

    # Check if --prod flag is present
    use_production = '--prod' in sys.argv

    if use_production:
        # Use Waitress for production
        try:
            from waitress import serve
            host = '0.0.0.0'
            port = 5000
            print(f"Starting production server with Waitress on {host}:{port}")
            print("Press CTRL+C to quit")
            serve(app, host=host, port=port, threads=4)
        except ImportError:
            print("ERROR: Waitress is not installed. Please install it with:")
            print("  pip install waitress")
            print("  or: uv pip install waitress")
            sys.exit(1)
    else:
        # Use Flask's built-in development server
        print("Starting development server (Flask built-in)")
        print("For production use: python run.py --prod")
        app.run(debug=cfg.app.debug, host='0.0.0.0')

if __name__ == '__main__':
    main()