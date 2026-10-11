# ERP01

A Python-based Enterprise Resource Planning (ERP) system.

## Description

ERP01 is an enterprise resource planning solution designed to help businesses manage and integrate their core processes efficiently.

## Features

- 📦 Modular architecture for easy customization
- 🔒 Secure authentication and authorization
- 📊 Real-time data analytics and reporting
- 🔄 Integration capabilities with third-party systems
- 💼 Multi-user support with role-based access control

## Installation

### Prerequisites

- Python 3.12 (matches CI and the devcontainer)
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/nyeinpyaesone-ui/erp01.git
cd erp01
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the application:
```bash
python main.py
```

## Usage

[Add usage instructions here]

## Project Structure

```
erp01/
├── main.py              # Application entry point
├── config/              # Configuration management
├── modules/             # ERP modules (base.py = BaseModule)
├── utils/               # Utility functions (logging, validation)
├── tests/               # Test cases (pytest)
├── scripts/             # Dev/maintenance automation
├── sprint_planning/     # Sprint documentation
├── docs/                # Documentation
└── .github/workflows/   # CI pipeline
```

## Development

### Running Tests

```bash
pytest
```

### Code Style

This project follows PEP 8 guidelines. To check code style:

```bash
flake8 .
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

**nyeinpyaesone-ui** - [GitHub Profile](https://github.com/nyeinpyaesone-ui)

## Acknowledgments

- [List any acknowledgments here]

---

*Built with using Python*
