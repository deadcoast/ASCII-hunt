#!/bin/bash

echo "Checking Markdown links in src/docs directory..."

# Make sure we have a valid config file
if [ ! -f .markdown-link-check.json ]; then
    echo '{
  "ignorePatterns": [
    {
      "pattern": "^Widget_Link$"
    }
  ],
  "replacementPatterns": [],
  "httpHeaders": [],
  "timeout": "20s"
}' > .markdown-link-check.json
fi

# Loop through each file individually
for file in $(find src/docs -name "*.md"); do
    echo "Checking $file..."
    npx markdown-link-check -q -c .markdown-link-check.json "$file"
    
    if [ $? -ne 0 ]; then
        echo "❌ Found broken links in $file"
        HAS_ERRORS=1
    fi
done

if [ "$HAS_ERRORS" == "1" ]; then
    echo "❌ Some links are broken. Please fix them."
    exit 1
else 
    echo "✅ All links are valid!"
fi
