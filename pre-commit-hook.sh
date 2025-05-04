#!/bin/bash

# Pre-commit hook to check for sensitive information in files being committed
# To install: cp pre-commit-hook.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit

echo "Running pre-commit checks for sensitive information..."

# Check for environment files that shouldn't be committed
ENV_FILES=$(git diff --cached --name-only | grep -E '\.env|\.env\.|\.env.*\.local|backend/\.env|frontend/\.env')
if [ -n "$ENV_FILES" ]; then
  echo "ERROR: Attempting to commit environment files that may contain secrets:"
  echo "$ENV_FILES"
  echo "Please remove these files from your commit."
  exit 1
fi

# Check for utility scripts that might contain hardcoded credentials
UTIL_SCRIPTS=$(git diff --cached --name-only | grep -E 'check_redis.*\.py|check_supabase\.py|create_bucket.*\.py|list_buckets\.py|check_db_connection\.py')
if [ -n "$UTIL_SCRIPTS" ]; then
  echo "WARNING: Attempting to commit utility scripts that might contain sensitive information:"
  echo "$UTIL_SCRIPTS"
  echo "Please ensure these files do not contain hardcoded credentials."
  
  # Check for potential API keys, tokens, or passwords in these files
  SENSITIVE_PATTERNS="(api[_-]?key|token|secret|password|credential|auth)"
  FOUND_SENSITIVE=$(git diff --cached -U0 | grep -E "$SENSITIVE_PATTERNS" | grep -v "os\.environ\.get\|load_dotenv")
  
  if [ -n "$FOUND_SENSITIVE" ]; then
    echo "ERROR: Found potential hardcoded credentials in files being committed:"
    echo "$FOUND_SENSITIVE"
    echo "Please remove hardcoded credentials and use environment variables instead."
    exit 1
  fi
  
  # Ask for confirmation
  read -p "Are you sure these files don't contain sensitive information? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Commit aborted."
    exit 1
  fi
fi

# Check all files for potential API keys, tokens, or passwords
ALL_FILES=$(git diff --cached --name-only)
for file in $ALL_FILES; do
  # Skip binary files and already checked utility scripts
  if [[ -f "$file" && ! "$file" =~ \.(jpg|jpeg|png|gif|ico|svg|woff|woff2|ttf|eot|mp3|mp4|mov|zip|tar|gz)$ && ! "$UTIL_SCRIPTS" =~ $file ]]; then
    # Check for JWT tokens
    JWT_PATTERN="eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}"
    JWT_FOUND=$(git diff --cached -U0 "$file" | grep -E "$JWT_PATTERN" | grep -v "os\.environ\.get\|load_dotenv")
    
    if [ -n "$JWT_FOUND" ]; then
      echo "ERROR: Found potential JWT token in $file:"
      echo "$JWT_FOUND"
      echo "Please remove hardcoded tokens and use environment variables instead."
      exit 1
    fi
    
    # Check for other sensitive patterns
    SENSITIVE_PATTERNS="(api[_-]?key|token|secret|password|credential|auth)[\"']?\s*[:=]\s*[\"'][a-zA-Z0-9_\-\.]{8,}[\"']"
    SENSITIVE_FOUND=$(git diff --cached -U0 "$file" | grep -E "$SENSITIVE_PATTERNS" | grep -v "os\.environ\.get\|load_dotenv")
    
    if [ -n "$SENSITIVE_FOUND" ]; then
      echo "ERROR: Found potential hardcoded credentials in $file:"
      echo "$SENSITIVE_FOUND"
      echo "Please remove hardcoded credentials and use environment variables instead."
      exit 1
    fi
  fi
done

echo "Pre-commit checks passed!"
exit 0
