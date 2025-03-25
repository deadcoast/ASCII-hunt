# Import Management with ImportMagic

This project uses ImportMagic to automatically manage Python imports. Here's how to use it:

## Available Tools

1. **Fix imports in a single file:**

```

python tools/fix_imports.py path/to/your/file.py

```

2. **Fix imports in the entire project:**

```

python tools/fix_project_imports.py .

```

3. **Use the pre-commit hook:**
   Import issues in staged Python files are automatically fixed when you commit.

## Best Practices

1. Run the project-wide fixer before major commits
2. Don't disable the pre-commit hook
3. Report any issues with the import fixing process

## Import Style Guide

We follow these import conventions:

- Standard library imports first
- Third-party library imports second
- Local module imports last
- Alphabetical ordering within each group
- Avoid wildcard imports (from module import \*)

### Schedule Regular Import Audits

Set up a regular schedule (maybe monthly) to run the import fixer across your entire codebase to catch any accumulated issues.

## Phase 8: Troubleshooting Guide

Create a troubleshooting guide for common ImportMagic issues:

# ImportMagic Troubleshooting

## Common Issues and Solutions

### 1. Missing imports not being detected

**Problem:** ImportMagic doesn't add imports for some modules you're using.

**Solution:**

- Make sure the module is installed in your environment
- Try rebuilding the symbol index
- Check if you're using a very uncommon or internal module

### 2. Script is too slow

**Problem:** The import fixer takes too long to run.

**Solution:**

- Build the index once and reuse it for multiple files
- Use the `--start-at-<module>` flag if available
- Run it only on changed files, not the entire project

### 3. Incorrect imports are being added

**Problem:** ImportMagic adds imports from the wrong module.

**Solution:**

- Be more specific in your code (e.g., use fully qualified names)
- Add explicit imports for ambiguous names
