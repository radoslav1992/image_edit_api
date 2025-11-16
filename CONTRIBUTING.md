# Contributing to Background Removal API

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## 🎯 How to Contribute

### Reporting Bugs

1. **Check existing issues** - Someone might have already reported it
2. **Create a detailed bug report** including:
   - Description of the bug
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Environment details (OS, Python version, etc.)
   - Error messages and logs

### Suggesting Features

1. **Check existing feature requests**
2. **Create a feature request** including:
   - Clear description of the feature
   - Use case and benefits
   - Proposed implementation (optional)
   - Examples or mockups (if applicable)

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Add tests** for new functionality
5. **Ensure all tests pass** (`python test_api.py`)
6. **Update documentation** if needed
7. **Commit your changes** (`git commit -m 'Add amazing feature'`)
8. **Push to the branch** (`git push origin feature/amazing-feature`)
9. **Open a Pull Request**

## 📝 Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/background_removal_api.git
cd background_removal_api

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your REPLICATE_API_TOKEN

# Run tests
python test_api.py
```

## 🧪 Testing Guidelines

- Write tests for all new features
- Ensure existing tests pass
- Aim for high code coverage
- Include both positive and negative test cases

## 📚 Documentation

- Update README.md for user-facing changes
- Add docstrings to all functions and classes
- Update API documentation comments
- Create examples for new features

## 💻 Code Style

- Follow PEP 8 style guide
- Use type hints where possible
- Write descriptive variable names
- Add comments for complex logic
- Keep functions focused and small

## 🔍 Code Review Process

1. Maintainer reviews your PR
2. Address any feedback
3. Once approved, PR will be merged
4. Your contribution will be acknowledged

## 🎖️ Recognition

Contributors will be:
- Listed in the README
- Mentioned in release notes
- Given credit in the project

## 📧 Questions?

Feel free to open an issue for any questions about contributing!

Thank you for making this project better! 🙏

