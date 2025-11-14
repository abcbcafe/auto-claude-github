#!/bin/bash
# Example: Create multiple repositories in batch

# List of projects to create
projects=(
  "web-frontend:Web frontend application"
  "api-backend:REST API backend service"
  "data-pipeline:Data processing pipeline"
  "ml-model:Machine learning model training"
)

# Base directory for projects
BASE_DIR="$HOME/projects"

echo "Creating ${#projects[@]} repositories..."

for project_info in "${projects[@]}"; do
  # Split by colon
  IFS=':' read -r name description <<< "$project_info"

  echo ""
  echo "Creating $name..."

  # Create with ClaudeUp
  claudeup "$name" \
    -d "$description" \
    -p "$BASE_DIR/$name"

  if [ $? -eq 0 ]; then
    echo "✓ Successfully created $name"
  else
    echo "✗ Failed to create $name"
  fi
done

echo ""
echo "Batch creation complete!"
echo "Projects created in: $BASE_DIR"
