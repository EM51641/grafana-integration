#!/bin/bash

# Colors for better output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Creating a private GitHub repository using GitHub CLI (gh)${NC}"

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}GitHub CLI (gh) is not installed.${NC}"
    echo -e "${YELLOW}Please install it first:${NC}"
    echo "  - macOS: brew install gh"
    echo "  - Linux: Follow instructions at https://github.com/cli/cli/blob/trunk/docs/install_linux.md"
    echo "  - Windows: winget install --id GitHub.cli"
    exit 1
fi

# Check if user is logged in to GitHub
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}You need to login to GitHub first.${NC}"
    echo -e "${BLUE}Running 'gh auth login'...${NC}"
    gh auth login
fi

# Ask for repository name
echo -e "${BLUE}Enter a name for your GitHub repository (default: otel-getting-started):${NC}"
read repo_name
repo_name=${repo_name:-otel-getting-started}

# Ask for repository description
echo -e "${BLUE}Enter a description for your repository (default: OpenTelemetry observability stack with Grafana):${NC}"
read repo_description
repo_description=${repo_description:-"OpenTelemetry observability stack with Grafana"}

# Create the repository
echo -e "${BLUE}Creating private GitHub repository: ${repo_name}...${NC}"
gh repo create "${repo_name}" --private --description "${repo_description}" --source=. --push

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Repository created and code pushed successfully!${NC}"
    
    # Get the repository URL
    repo_url=$(gh repo view --json url -q .url)
    echo -e "${GREEN}Your repository is available at: ${repo_url}${NC}"
else
    echo -e "${RED}Failed to create repository.${NC}"
    echo -e "${YELLOW}You can try manually with:${NC}"
    echo "  gh repo create ${repo_name} --private --description \"${repo_description}\" --source=. --push"
fi

echo -e "${BLUE}Setup complete!${NC}" 