# Package Integrity Checker

A tool to check the integrity of Python packages by comparing installed files with files directly from the source repository.

## Usage

```bash
checker <package-name>
```

Install requirements first:

```bash
pip install -r requirements.txt
```

## How It Works

1. Fetches package info from PyPI
2. Downloads the source code from the repository
3. Compares installed package files with source files
4. Generates a report showing differences

## Requirements

- Python 3.6+
- PyYAML
- requests

## License

MIT
