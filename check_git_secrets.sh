#!/bin/bash

# Script to check for passwords and secrets in Git history
# This script will search for common patterns that might indicate secrets

# Text colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Checking Git History for Secrets ===${NC}"
echo -e "${YELLOW}This script will search for common patterns that might indicate secrets in your Git history.${NC}"
echo -e "${YELLOW}If any secrets are found, you should change them immediately and remove them from Git history.${NC}"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}Git is not installed. Please install Git before continuing.${NC}"
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --is-inside-work-tree &> /dev/null; then
    echo -e "${RED}Not in a Git repository. Please run this script from within a Git repository.${NC}"
    exit 1
fi

echo -e "${BLUE}Searching for password patterns...${NC}"
PASSWORD_RESULTS=$(git log -p | grep -i -E 'password|passwd|pass' | grep -v 'password.*\[.*\]' | grep -v '# password' | grep -v 'password.*placeholder')
if [ -n "$PASSWORD_RESULTS" ]; then
    echo -e "${RED}Found potential password references:${NC}"
    echo "$PASSWORD_RESULTS" | head -n 20
    if [ $(echo "$PASSWORD_RESULTS" | wc -l) -gt 20 ]; then
        echo -e "${YELLOW}... and more. Total lines: $(echo "$PASSWORD_RESULTS" | wc -l)${NC}"
    fi
else
    echo -e "${GREEN}No obvious password patterns found.${NC}"
fi
echo ""

echo -e "${BLUE}Searching for secret key patterns...${NC}"
SECRET_RESULTS=$(git log -p | grep -i -E 'secret|key|token|auth|api.?key' | grep -v 'secret.*\[.*\]' | grep -v '# secret' | grep -v 'secret.*placeholder')
if [ -n "$SECRET_RESULTS" ]; then
    echo -e "${RED}Found potential secret key references:${NC}"
    echo "$SECRET_RESULTS" | head -n 20
    if [ $(echo "$SECRET_RESULTS" | wc -l) -gt 20 ]; then
        echo -e "${YELLOW}... and more. Total lines: $(echo "$SECRET_RESULTS" | wc -l)${NC}"
    fi
else
    echo -e "${GREEN}No obvious secret key patterns found.${NC}"
fi
echo ""

echo -e "${BLUE}Searching for database connection strings...${NC}"
DB_RESULTS=$(git log -p | grep -i -E 'database_url|db_url|connection|jdbc|mongodb|postgresql|mysql|redis' | grep -v 'database_url.*\[.*\]' | grep -v '# database' | grep -v 'database.*placeholder')
if [ -n "$DB_RESULTS" ]; then
    echo -e "${RED}Found potential database connection strings:${NC}"
    echo "$DB_RESULTS" | head -n 20
    if [ $(echo "$DB_RESULTS" | wc -l) -gt 20 ]; then
        echo -e "${YELLOW}... and more. Total lines: $(echo "$DB_RESULTS" | wc -l)${NC}"
    fi
else
    echo -e "${GREEN}No obvious database connection strings found.${NC}"
fi
echo ""

echo -e "${BLUE}Searching for AWS credentials...${NC}"
AWS_RESULTS=$(git log -p | grep -i -E 'aws|amazon|s3|ec2|iam|AKIA[A-Z0-9]{16}')
if [ -n "$AWS_RESULTS" ]; then
    echo -e "${RED}Found potential AWS credentials:${NC}"
    echo "$AWS_RESULTS" | head -n 20
    if [ $(echo "$AWS_RESULTS" | wc -l) -gt 20 ]; then
        echo -e "${YELLOW}... and more. Total lines: $(echo "$AWS_RESULTS" | wc -l)${NC}"
    fi
else
    echo -e "${GREEN}No obvious AWS credentials found.${NC}"
fi
echo ""

echo -e "${BLUE}Searching for private keys...${NC}"
PRIVATE_KEY_RESULTS=$(git log -p | grep -i -E '-----BEGIN .* PRIVATE KEY-----|ssh-rsa')
if [ -n "$PRIVATE_KEY_RESULTS" ]; then
    echo -e "${RED}Found potential private keys:${NC}"
    echo "$PRIVATE_KEY_RESULTS" | head -n 20
    if [ $(echo "$PRIVATE_KEY_RESULTS" | wc -l) -gt 20 ]; then
        echo -e "${YELLOW}... and more. Total lines: $(echo "$PRIVATE_KEY_RESULTS" | wc -l)${NC}"
    fi
else
    echo -e "${GREEN}No obvious private keys found.${NC}"
fi
echo ""

echo -e "${BLUE}Searching for JWT tokens...${NC}"
JWT_RESULTS=$(git log -p | grep -i -E 'eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*')
if [ -n "$JWT_RESULTS" ]; then
    echo -e "${RED}Found potential JWT tokens:${NC}"
    echo "$JWT_RESULTS" | head -n 20
    if [ $(echo "$JWT_RESULTS" | wc -l) -gt 20 ]; then
        echo -e "${YELLOW}... and more. Total lines: $(echo "$JWT_RESULTS" | wc -l)${NC}"
    fi
else
    echo -e "${GREEN}No obvious JWT tokens found.${NC}"
fi
echo ""

echo -e "${BLUE}=== Summary ===${NC}"
echo -e "${YELLOW}If any secrets were found, you should:${NC}"
echo -e "1. ${RED}Change the credentials immediately${NC}"
echo -e "2. ${YELLOW}Remove them from Git history using:${NC}"
echo -e "   git filter-branch --force --index-filter \\"
echo -e "   \"git rm --cached --ignore-unmatch PATH-TO-FILE\" \\"
echo -e "   --prune-empty --tag-name-filter cat -- --all"
echo -e "3. ${YELLOW}Force push to overwrite the remote repository:${NC}"
echo -e "   git push origin --force --all"
echo ""
echo -e "${BLUE}For more information, see SECURE_PASSWORDS.md${NC}"
