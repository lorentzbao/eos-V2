# EOS Configuration Guide

Hydra-based configuration management for flexible application deployment and development.

## 🚀 Quick Start

```bash
# Default configuration
uv run python run.py

# Override specific settings
uv run python run.py app.debug=false index.dir=data/production/index

# Use custom configuration file
uv run python run.py --config-path custom/ --config-name production
```

## 📁 Configuration Structure

```
conf/
└── config.yaml          # Default configuration
```

### **Default Configuration** (`conf/config.yaml`)

```yaml
app:
  secret_key: "your-secret-key-here"
  debug: true

index:
  dir: "data/whoosh_index"
```

## 🛠️ Configuration Options

### **Application Settings** (`app`)

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `secret_key` | string | `"your-secret-key-here"` | Flask session secret key |
| `debug` | boolean | `true` | Enable Flask debug mode |

### **Index Settings** (`index`)

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `dir` | string | `"data/whoosh_index"` | Whoosh search index directory |

## 📖 Usage Examples

### **Command Line Overrides**

```bash
# Disable debug mode
uv run python run.py app.debug=false

# Custom index directory
uv run python run.py index.dir=data/custom_index/

# Multiple overrides
uv run python run.py app.debug=false index.dir=data/prod/ app.secret_key=production-secret
```

### **Custom Configuration Files**

Create additional configuration files for different environments:

```bash
# Create production config
mkdir -p conf/env/
cat > conf/env/production.yaml << 'EOF'
app:
  secret_key: "production-secret-key-change-me"
  debug: false

index:
  dir: "data/production/whoosh_index"
EOF

# Use production config
uv run python run.py --config-path conf/env --config-name production
```

### **Development vs Production**

```bash
# Development (default)
uv run python run.py

# Production deployment
uv run python run.py \
  app.debug=false \
  app.secret_key=secure-production-key \
  index.dir=data/production/whoosh_index
```

## 🏗️ Advanced Configuration

### **Environment-specific Configurations**

```yaml
# conf/env/development.yaml
app:
  secret_key: "dev-secret-key"
  debug: true

index:
  dir: "data/dev/whoosh_index"

# conf/env/staging.yaml  
app:
  secret_key: "staging-secret-key"
  debug: false

index:
  dir: "data/staging/whoosh_index"

# conf/env/production.yaml
app:
  secret_key: "production-secret-key"
  debug: false

index:
  dir: "data/production/whoosh_index"
```

Usage:
```bash
uv run python run.py --config-path conf/env --config-name development
uv run python run.py --config-path conf/env --config-name staging
uv run python run.py --config-path conf/env --config-name production
```

### **Docker Deployment Configuration**

```yaml
# conf/docker.yaml
app:
  secret_key: "${SECRET_KEY}"
  debug: false

index:
  dir: "/app/data/whoosh_index"
```

```bash
# Use with environment variables
export SECRET_KEY=my-docker-secret
uv run python run.py --config-name docker
```

## 🔧 Integration with Application

The configuration is automatically injected into the Flask application:

```python
# run.py
import hydra
from omegaconf import DictConfig
from app import create_app

@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg: DictConfig) -> None:
    app = create_app(cfg)
    app.run(debug=cfg.app.debug, host='0.0.0.0')

if __name__ == '__main__':
    main()
```

```python
# app/__init__.py
def create_app(config=None):
    app = Flask(__name__)
    
    if config:
        # Hydra configuration
        app.config['SECRET_KEY'] = config.app.secret_key
        app.config['INDEX_DIR'] = config.index.dir
    else:
        # Fallback defaults
        app.config['SECRET_KEY'] = 'fallback-secret-key'
        app.config['INDEX_DIR'] = 'data/whoosh_index'
    
    return app
```

## 📋 Best Practices

1. **Security**: Never commit production secrets to version control
2. **Environment Variables**: Use environment variable substitution for sensitive data
3. **Default Values**: Provide sensible defaults in the base configuration
4. **Validation**: Use Hydra's structured configs for type validation when needed
5. **Documentation**: Document all configuration options and their effects

## 🔍 Debugging Configuration

```bash
# Print resolved configuration
uv run python -c "
import hydra
from omegaconf import DictConfig, OmegaConf

@hydra.main(version_base=None, config_path='conf', config_name='config')
def print_config(cfg: DictConfig):
    print(OmegaConf.to_yaml(cfg))

if __name__ == '__main__':
    print_config()
"

# Check specific override
uv run python -c "..." app.debug=false index.dir=custom/
```

This flexible configuration system allows EOS to adapt to different deployment environments while maintaining clean separation between application logic and configuration management.