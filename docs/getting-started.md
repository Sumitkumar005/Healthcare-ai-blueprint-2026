# Getting Started Guide

Welcome to Healthcare AI Blueprint 2026! This guide will help you get started with any project in this repository.

## Prerequisites

### Required Software

1. **Python 3.9+**
   - Download from [python.org](https://www.python.org/downloads/)
   - Verify: `python --version`

2. **Git**
   - Download from [git-scm.com](https://git-scm.com/downloads)
   - Verify: `git --version`

3. **Node.js 16+** (for React projects only)
   - Download from [nodejs.org](https://nodejs.org/)
   - Verify: `node --version`

### Free API Keys

Most projects use free AI APIs. Get your keys:

1. **Groq** (Recommended - Fastest, Free)
   - Visit: https://groq.com
   - Sign up for free account
   - Get API key from dashboard

2. **OpenRouter** (Many Free Models)
   - Visit: https://openrouter.ai
   - Sign up for free tier
   - Get API key

3. **Together AI** (Alternative)
   - Visit: https://together.ai
   - Free tier available

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/healthcare-ai-blueprint-2026.git
cd healthcare-ai-blueprint-2026
```

### 2. Choose a Project

Browse the [main README](../README.md) to find a project that interests you.

### 3. Set Up the Project

```bash
# Navigate to project folder
cd 01-voice-to-clinical-note

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys
```

### 4. Run the Project

```bash
# For Python projects
python src/main.py

# For projects with frontend
# Terminal 1: Backend
python src/main.py

# Terminal 2: Frontend (if React)
cd frontend
npm install
npm start
```

## Project Structure

Each project follows this structure:

```
XX-project-name/
├── README.md              # Project documentation
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variable template
├── src/                  # Main application code
│   ├── main.py          # Entry point
│   └── ...
├── tests/               # Unit tests
├── examples/            # Sample inputs/outputs
└── frontend/            # Web interface (if applicable)
```

## Common Issues

### Import Errors

If you get import errors:
```bash
# Make sure you're in the project directory
cd XX-project-name

# Reinstall dependencies
pip install -r requirements.txt
```

### API Key Errors

If you get API key errors:
1. Check `.env` file exists
2. Verify API key is correct
3. Ensure no extra spaces in `.env` file
4. Restart the application

### Port Already in Use

If port 8000 (or other) is in use:
```bash
# Find and kill the process
# On Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# On macOS/Linux:
lsof -ti:8000 | xargs kill
```

## Next Steps

- Read the project-specific README.md
- Check the examples/ folder for sample data
- Review the code comments
- Try modifying the code to understand it better

## Getting Help

- Check project README.md
- Review [Tech Stack Guide](tech-stack-guide.md)
- Open an issue on GitHub
- Check GitHub Discussions

Happy coding! 🚀


