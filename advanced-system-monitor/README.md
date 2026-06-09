# MyProject - Modular Python Application

A small modular Python project demonstrating layered architecture with logging, configuration, and subsystems.

## Project Structure

```
MyProject/
├── core/
│   ├── __init__.py
│   ├── config.py          # Configuration settings
│   ├── logger.py          # Logging setup
│   └── exceptions.py      # Custom exceptions
├── subsystems/
│   ├── __init__.py
│   ├── network.py         # Network operations
│   └── sysstat.py         # System statistics
├── tests/
│   ├── __init__.py
│   └── test_network.py    # Network tests
├── utils/
│   ├── __init__.py
│   └── helpers.py         # Helper functions
├── main.py                # Entry point
└── README.md
```

## How to Run

```bash
cd MyProject
python main.py
```

## Running Tests

```bash
python -m unittest tests.test_network
```

## Features

- **Core Layer**: Configuration, logging, and exception handling
- **Subsystem Layer**: Network operations and system statistics
- **Test Layer**: Unit tests for core functionality
- **Utilities**: Helper functions for formatting and common operations

## Modules

### Core
- `config.py`: Centralized configuration
- `logger.py`: Logging setup with custom formatting
- `exceptions.py`: Custom application exceptions

### Subsystems
- `network.py`: Network connectivity checks
- `sysstat.py`: System information and statistics

### Utils
- `helpers.py`: Utility functions
