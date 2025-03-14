#!/bin/bash

# Colors for better output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Setting up a private Git repository for your OpenTelemetry project${NC}"

# Initialize Git repository if not already initialized
if [ ! -d .git ]; then
    echo -e "${BLUE}Initializing Git repository...${NC}"
    git init
    echo -e "${GREEN}Git repository initialized!${NC}"
else
    echo -e "${GREEN}Git repository already initialized!${NC}"
fi

# Create .gitignore file
if [ ! -f .gitignore ]; then
    echo -e "${BLUE}Creating .gitignore file...${NC}"
    cat > .gitignore << EOF
# Environment variables
.env

# Docker volumes
*-data/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# IDE files
.idea/
.vscode/
*.swp
*.swo

# OS specific
.DS_Store
Thumbs.db
EOF
    echo -e "${GREEN}.gitignore file created!${NC}"
fi

# Add all files to Git
echo -e "${BLUE}Adding files to Git...${NC}"
git add .

# Commit changes
echo -e "${BLUE}Committing files...${NC}"
git commit -m "Initial commit of OpenTelemetry project"

# Ask for remote repository URL
echo -e "${BLUE}Please enter the URL of your private Git repository (e.g., https://github.com/username/repo.git):${NC}"
read repo_url

if [ -z "$repo_url" ]; then
    echo -e "${BLUE}No repository URL provided. You can add it later with:${NC}"
    echo "git remote add origin YOUR_REPOSITORY_URL"
    echo "git push -u origin main"
else
    # Add remote repository
    echo -e "${BLUE}Adding remote repository...${NC}"
    git remote add origin $repo_url

    # Push to remote repository
    echo -e "${BLUE}Pushing to remote repository...${NC}"
    git push -u origin main || git push -u origin master

    echo -e "${GREEN}Successfully pushed to remote repository!${NC}"
fi

echo -e "${GREEN}Setup complete!${NC}"
echo -e "${BLUE}If you haven't created a private repository yet, you can create one at:${NC}"
echo "- GitHub: https://github.com/new"
echo "- GitLab: https://gitlab.com/projects/new"
echo "- Bitbucket: https://bitbucket.org/repo/create"

echo -e "${BLUE}After creating the repository, run:${NC}"
echo "git remote add origin YOUR_REPOSITORY_URL"
echo "git push -u origin main" 