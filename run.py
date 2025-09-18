import hydra
from omegaconf import DictConfig
from app import create_app

@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg: DictConfig) -> None:
    app = create_app(cfg)
    app.run(debug=cfg.app.debug, host='0.0.0.0')

if __name__ == '__main__':
    main()