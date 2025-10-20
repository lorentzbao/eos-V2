import hydra
from omegaconf import DictConfig
from app import create_app
import sys

@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg: DictConfig) -> None:
    app = create_app(cfg)

    # Get server configuration
    server_type = cfg.server.type
    host = cfg.server.host
    port = cfg.server.port

    if server_type == 'production':
        # Use Waitress for production
        try:
            from waitress import serve
            threads = cfg.server.threads
            print("=" * 60)
            print(f"Starting PRODUCTION server with Waitress")
            print(f"  Host: {host}")
            print(f"  Port: {port}")
            print(f"  Threads: {threads}")
            print(f"  URL: http://{host}:{port}")
            print("=" * 60)
            print("Press CTRL+C to quit")
            serve(app, host=host, port=port, threads=threads)
        except ImportError:
            print("ERROR: Waitress is not installed. Please install it with:")
            print("  uv pip install waitress")
            sys.exit(1)
    else:
        # Use Flask's built-in development server
        print("=" * 60)
        print(f"Starting DEVELOPMENT server (Flask built-in)")
        print(f"  Host: {host}")
        print(f"  Port: {port}")
        print(f"  Debug: {cfg.app.debug}")
        print(f"  URL: http://{host}:{port}")
        print("=" * 60)
        print("For production, use: uv run run.py server.type=production")
        app.run(debug=cfg.app.debug, host=host, port=port)

if __name__ == '__main__':
    main()