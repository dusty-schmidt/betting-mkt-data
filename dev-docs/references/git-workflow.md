# Git Workflow Cheatsheet

## Quick Reference

### Automated Workflow (Recommended)
```bash
# Start work session
./dev-workflow.sh start

# End work session  
./dev-workflow.sh end

# Check status
./dev-workflow.sh status
```

### Manual Commands

#### Daily Workflow
```bash
# 1. Start: Pull latest changes
git pull origin main

# 2. Work: Make your changes
git add -A
git commit -m "descriptive message"

# 3. End: Push changes
git push origin main
```

#### Branch Management (Future Use)
```bash
# Create feature branch
git checkout -b feature-name
# or
./dev-workflow.sh branch feature-name

# Switch branches
git checkout main
git checkout feature-name

# Merge feature branch
git checkout main
git merge feature-name
git branch -d feature-name  # Delete local branch
```

## Work Log Integration

### Automatic Work Logs
- **Created**: When running `./dev-workflow.sh start`
- **Location**: `dev-docs/work-logs/YYYY-MM-DD-task-name.md`
- **Status**: Automatically updated to "Completed" on `./dev-workflow.sh end`
- **Cleanup**: Work logs older than 7 days are automatically removed

### Manual Work Log Creation
```bash
# If you need to create manually
cp dev-docs/work-logs/TEMPLATE.md dev-docs/work-logs/$(date +%Y-%m-%d)-task-name.md
```

## Commit Message Format

**Automated**: `{task-name}: {date} completion`

**Manual**: Use descriptive, imperative messages:
- ✅ `add logging to database connection`
- ✅ `fix thread safety issue in orchestration`
- ❌ `fixed bug` or `updates`

## Common Scenarios

### Working with Agents
```bash
# Agent starts work
./dev-workflow.sh start
# → Creates work log, pulls changes

# Agent works on changes
# → Makes commits as needed

# Agent completes work  
./dev-workflow.sh end
# → Updates work log, commits final changes, pushes
```

### Handling Conflicts
```bash
# When git push fails due to conflicts
git pull origin main
# → Resolve conflicts in files
git add -A
git commit -m "resolve merge conflicts"
git push origin main
```

### Emergency Changes
```bash
# For hotfixes that can't wait for workflow script
git add -A
git commit -m "hotfix: urgent fix description"
git push origin main
# → Update work log manually if needed
```

## File Management

### What to Commit
- ✅ Source code changes
- ✅ Documentation updates  
- ✅ Configuration changes
- ✅ Work logs

### What NOT to Commit
- ❌ Database files (`*.db`)
- ❌ Log files (`logs/`)
- ❌ Python cache (`__pycache__/`, `*.pyc`)
- ❌ Environment files (`.env`)
- ❌ IDE files (`.vscode/`, `.idea/`)

## Best Practices

### For Single Developer + Agents
1. **Always use workflow script** for consistency
2. **Keep work logs** - they provide excellent project history
3. **Pull before starting** - prevents conflicts
4. **Commit often** - automated script handles this
5. **Clear commit messages** - helps track what changed when

### For Future Team Development
1. **Use feature branches** for new features
2. **Pull requests** for code review
3. **Squash commits** before merging
4. **Tag releases** for version management

## Troubleshooting

### Script Not Working
```bash
# Make sure script is executable
chmod +x dev-workflow.sh

# Check git status
git status

# Check current branch
git branch --show-current
```

### Work Log Issues
```bash
# Find in-progress work logs
find dev-docs/work-logs/ -name "*.md" -exec grep -l "Status.*In Progress" {} \;

# Clean up stuck work logs manually
# Edit the file and change status to "Completed" or "Blocked"
```

### Git Issues
```bash
# Reset to clean state (CAREFUL - destroys uncommitted changes)
git reset --hard HEAD

# Check what files are different from last commit
git diff --name-only

# See commit history
git log --oneline -10
```

## Integration with Development Tasks

### Adding New Provider
```bash
# 1. Start work
./dev-workflow.sh start

# 2. Follow docs/PROVIDERS.md
# 3. Create provider files
# 4. Test locally
# 5. End work
./dev-workflow.sh end
```

### Fixing Known Issues
```bash
# 1. Check dev-docs/TASKS.md for priorities
# 2. Start work
./dev-workflow.sh start  
# 3. Fix the issue
# 4. End work
./dev-workflow.sh end
```

The workflow script handles most complexity automatically - only use manual git commands when you need something specific or the script isn't working.