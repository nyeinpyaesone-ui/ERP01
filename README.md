# ERP01

A Python-based Enterprise Resource Planning (ERP) system with a modern web interface.

## Description

ERP01 is an enterprise resource planning solution designed to help businesses manage and integrate their core processes efficiently. It features a modular architecture and includes both CLI and web-based interfaces.

## Features

- Modular architecture for easy customization
- Secure authentication and authorization
- Real-time data analytics and reporting
- Integration capabilities with third-party systems
- Multi-user support with role-based access control
- Modern, responsive web interface
- Mobile-friendly dashboard
- RESTful API endpoints

## Installation

### Prerequisites

- Python 3.8 or higher
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

**CLI Mode:**
```bash
python main.py
```

**Web Interface Mode:**
```bash
# Set USE_WEB=true in your .env file, then run:
python main.py
```

The web interface will be available at http://localhost:5000

## Usage

### CLI Mode

Run the application in command-line mode:

```bash
python main.py
```

This will display system information and status in the terminal.

### Web Interface

To enable the web interface, set `USE_WEB=true` in your `.env` file:

```env
USE_WEB=true
```

Then run the application:

```bash
python main.py
```

Access the web dashboard at http://localhost:5000

#### Web Features

- **Dashboard**: View key metrics and statistics
- **Navigation**: Access different modules (Inventory, Finance, HR, etc.)
- **Real-time Updates**: Dynamic module status updates
- **Responsive Design**: Works on desktop and mobile devices
- **API Endpoints**: 
  - `/api/status` - System status
  - `/api/modules` - Module information

## Project Structure

```
erp01/
├── main.py              # Application entry point
├── config/              # Configuration files
├── modules/             # ERP modules
├── utils/               # Utility functions
├── web/                 # Web interface
│   ├── __init__.py      # Flask app factory
│   ├── routes/          # URL routes
│   ├── templates/       # HTML templates
│   └── static/          # CSS, JS, images
│       ├── css/
│       └── js/
├── tests/               # Test cases
└── docs/                # Documentation
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

To format code automatically:

```bash
black .
```

### Adding New Modules

1. Create a new module in the `modules/` directory
2. Implement the `BaseModule` interface
3. Add routes in `web/routes/` if web access is needed
4. Update tests accordingly

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| APP_NAME | Application name | ERP01 |
| APP_ENV | Environment (development/production) | development |
| DEBUG | Enable debug mode | True |
| DATABASE_URL | Database connection string | sqlite:///erp01.db |
| SECRET_KEY | Secret key for sessions | dev-secret-key |
| LOG_LEVEL | Logging level | INFO |
| USE_WEB | Enable web interface | False |

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

**nyeinpysone-ui** - [GitHub Profile](https://github.com/nyeinpyaesone-ui)

## Acknowledgments

- Flask web framework
- Modern UI design patterns
- Enterprise software best practices

---

*Built with Python and Flask*
