# 🚀 Universal Python Project Setup

This repository now uses a clean, standardized approach for Python virtual environment management across all projects.

## 🎯 Philosophy

- **Fresh Environment**: Each project gets its own isolated virtual environment
- **No Shared Dependencies**: Eliminates dependency conflicts between projects
- **Reproducible Setups**: Requirements are always installed fresh from requirements.txt
- **Consistent Approach**: Same setup process across all projects

## 📁 Setup Structure

```
Projects/
├── setup_python_env.sh          # Universal setup script
├── setup_all_projects.sh         # Master setup for all projects
├── AgenTech Research Hub/
│   ├── setup.sh                  # Project-specific setup
│   ├── requirements.txt
│   └── .venv/                    # Project virtual environment
├── agentic-finance-workflow/
│   ├── setup.sh
│   ├── requirements.txt
│   └── .venv/
└── ... (other projects)
```

## 🛠️ Usage

### Setup Individual Project

```bash
# Navigate to any project
cd "AgenTech Research Hub"

# Run project setup
./setup.sh

# Activate environment
source .venv/bin/activate

# Start developing!
```

### Setup All Projects at Once

```bash
# From the Projects root directory
./setup_all_projects.sh
```

### Manual Setup with Universal Script

```bash
# Navigate to any project without setup.sh
cd "Your Project"

# Run universal setup
../setup_python_env.sh

# Activate environment
source .venv/bin/activate
```

## 🔧 What Each Setup Does

1. **Removes** any existing `.venv` directory
2. **Creates** fresh Python virtual environment
3. **Upgrades** pip to latest version
4. **Installs** requirements from:
   - `requirements-production.txt` (priority)
   - `requirements.production.txt` 
   - `requirements.txt` (fallback)
5. **Installs** common development tools
6. **Creates** necessary project directories
7. **Provides** activation instructions

## 📦 Project-Specific Features

Each project's `setup.sh` includes:
- Universal Python environment setup
- Project-specific dependencies
- Required directory creation
- Custom configuration
- Usage instructions

## ✅ Benefits

- **🔒 Isolation**: No dependency conflicts between projects
- **🔄 Reproducible**: Fresh setup every time
- **🧹 Clean**: No shared bloat or old dependencies
- **📋 Standardized**: Consistent approach across all projects
- **🚀 Fast**: Quick setup with clear instructions
- **🛡️ Safe**: Each project is self-contained

## 🗑️ Cleanup

To reset any project:

```bash
cd "Project Name"
rm -rf .venv
./setup.sh
```

## 📊 Current Projects

- ✅ **AgenTech Research Hub** - AI research platform
- ✅ **Agentic Finance Workflow** - Financial analysis system  
- ✅ **AI Data Analytics Agent** - Data analytics platform
- ✅ **MedAssist AI MCP** - Medical AI assistant
- ✅ **Multi-Agent Content Analytics** - Content analysis system
- ✅ **Microsoft Stock Price Prediction** - Stock prediction workflow

All projects now follow this standardized setup approach! 🎉
