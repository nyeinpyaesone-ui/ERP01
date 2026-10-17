# ERP01 Documentation

## Table of Contents
- [Getting Started](#getting-started)
- [Architecture](#architecture)
- [Modules](#modules)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Contributing](#contributing)

## Getting Started

### Prerequisites
- Python 3.12 (matches CI and the devcontainer)
- pip

### Installation
```bash
pip install -r requirements.txt
```

### Running the Application
```bash
python main.py
```

## Architecture

ERP01 follows a modular architecture with the following structure:
- `modules/` - Core business logic modules
- `config/` - Configuration management
- `utils/` - Utility functions and helpers
- `tests/` - Test suite
- `docs/` - Documentation

## Modules

### BaseModule
All ERP modules inherit from `BaseModule` which provides:
- Initialization lifecycle
- Configuration validation
- Execution interface

## Configuration

Configuration is managed through environment variables. Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request
