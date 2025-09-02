#!/bin/bash

# Master Setup Script for All Projects
# This script sets up virtual environments for all Python projects

echo "🌟 Master Project Setup Script"
echo "============================="

PROJECTS=(
    "AgenTech Research Hub"
    "agentic-finance-workflow"
    "AI Data Analytics Agent"
    "MedAssist Al MCP"
    "Multi-Agent-Content-Analytics"
)

echo "🎯 Found ${#PROJECTS[@]} Python projects to set up:"
for project in "${PROJECTS[@]}"; do
    echo "   📁 $project"
done

echo ""
read -p "🤔 Do you want to set up all projects? (y/N): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Setup cancelled."
    exit 1
fi

SETUP_COUNT=0
FAILED_COUNT=0

for project in "${PROJECTS[@]}"; do
    echo ""
    echo "🔄 Setting up: $project"
    echo "----------------------------------------"
    
    if [ -d "$project" ]; then
        cd "$project"
        if [ -f "setup.sh" ]; then
            if ./setup.sh; then
                echo "✅ $project setup completed successfully!"
                ((SETUP_COUNT++))
            else
                echo "❌ $project setup failed!"
                ((FAILED_COUNT++))
            fi
        else
            echo "⚠️  No setup.sh found for $project, running universal setup..."
            if ../setup_python_env.sh; then
                echo "✅ $project basic setup completed!"
                ((SETUP_COUNT++))
            else
                echo "❌ $project setup failed!"
                ((FAILED_COUNT++))
            fi
        fi
        cd ..
    else
        echo "❌ Directory '$project' not found!"
        ((FAILED_COUNT++))
    fi
done

echo ""
echo "🎉 Setup Summary"
echo "================"
echo "✅ Successfully set up: $SETUP_COUNT projects"
echo "❌ Failed setups: $FAILED_COUNT projects"
echo "📦 Total projects: ${#PROJECTS[@]}"

if [ $FAILED_COUNT -eq 0 ]; then
    echo ""
    echo "🚀 All projects are ready for development!"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Navigate to any project directory"
    echo "   2. Run: source .venv/bin/activate"
    echo "   3. Start developing!"
else
    echo ""
    echo "⚠️  Some projects failed to set up. Please check the errors above."
fi
