# Contributing to Healthcare AI Blueprint 2026

Thank you for your interest in contributing! This repository aims to be the go-to resource for healthcare AI developers, and your contributions make that possible.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)

### Suggesting New Projects

We welcome suggestions for new healthcare AI projects! Please open an issue with:
- Problem statement (what healthcare problem does this solve?)
- Proposed solution
- Difficulty level (Easy/Medium/Hard)
- Estimated complexity

### Adding New Projects

1. **Fork the repository**
2. **Create a new project folder** following the naming convention: `XX-project-name`
3. **Follow the project structure**:
   ```
   XX-project-name/
   ├── README.md
   ├── requirements.txt
   ├── .env.example
   ├── src/
   ├── tests/
   ├── examples/
   └── frontend/ (if applicable)
   ```
4. **Ensure code quality**:
   - Type hints for all functions
   - Docstrings for all classes/functions
   - Error handling
   - Logging instead of print
   - Tests (at least basic unit tests)
5. **Update main README.md** with your project
6. **Submit a pull request**

### Improving Existing Projects

- Fix bugs
- Add features
- Improve documentation
- Add examples
- Enhance error handling
- Add tests

## Code Style

### Python

- Follow PEP 8
- Use type hints
- Write docstrings (Google style)
- Maximum line length: 100 characters
- Use `black` for formatting (optional but recommended)

### JavaScript

- Use ES6+ syntax
- Follow Airbnb JavaScript Style Guide
- Use meaningful variable names
- Comment complex logic

## Project Requirements Checklist

Before submitting, ensure your project has:

- [ ] Comprehensive README.md
- [ ] requirements.txt with pinned versions
- [ ] .env.example file
- [ ] At least 3 example inputs/outputs
- [ ] Basic unit tests
- [ ] Error handling
- [ ] No hardcoded credentials
- [ ] Works with free APIs only
- [ ] Privacy/security notes in README
- [ ] Links back to main README

## Pull Request Process

1. Update README.md if needed
2. Add tests for new functionality
3. Ensure all tests pass
4. Update documentation
5. Submit PR with clear description

## Questions?

Open an issue with the `question` label, and we'll help you out!

Thank you for contributing to healthcare AI! 🚀


