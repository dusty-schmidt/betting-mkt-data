#!/bin/bash

# Unified Development Workflow Script
# Handles git operations + work-log automation for agent-friendly development

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_LOGS_DIR="$SCRIPT_DIR/dev-docs/work-logs"
TEMPLATE_FILE="$WORK_LOGS_DIR/TEMPLATE.md"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to get current date in YYYY-MM-DD format
get_current_date() {
    date +%Y-%m-%d
}

# Function to get current datetime for work-logs
get_current_datetime() {
    date +"%Y-%m-%d %H:%M:%S"
}

# Function to generate task name from git status
generate_task_name() {
    local task_name=""
    
    # Check for staged files
    local staged_files=$(git diff --cached --name-only)
    if [[ -n "$staged_files" ]]; then
        # Get the first staged file and extract meaningful name
        local first_file=$(echo "$staged_files" | head -n1)
        task_name=$(basename "$first_file" | sed 's/\.[^.]*$//' | sed 's/[-_]/ /g' | sed 's/\b\w/\U&/g')
    fi
    
    # If no staged files, check for modified files
    if [[ -z "$task_name" ]]; then
        local modified_files=$(git diff --name-only)
        if [[ -n "$modified_files" ]]; then
            local first_file=$(echo "$modified_files" | head -n1)
            task_name=$(basename "$first_file" | sed 's/\.[^.]*$//' | sed 's/[-_]/ /g' | sed 's/\b\w/\U&/g')
        fi
    fi
    
    # If still no name, use timestamp
    if [[ -z "$task_name" ]]; then
        task_name="work-session-$(date +%H%M)"
    fi
    
    echo "$task_name"
}

# Function to create work-log from template
create_work_log() {
    local task_name="$1"
    local date=$(get_current_date)
    local filename="${date}-${task_name,,}.md"
    local filepath="$WORK_LOGS_DIR/$filename"
    
    if [[ ! -f "$TEMPLATE_FILE" ]]; then
        log_error "Template file not found: $TEMPLATE_FILE"
        return 1
    fi
    
    if [[ -f "$filepath" ]]; then
        log_warning "Work log already exists: $filename"
        echo "$filepath"
        return 0
    fi
    
    # Create work log from template
    sed -e "s/\[Task Name\]/$task_name/" \
        -e "s/YYYY-MM-DD/$date/" \
        -e "s/In Progress | Completed | Blocked/In Progress/" \
        "$TEMPLATE_FILE" > "$filepath"
    
    log_success "Created work log: $filename"
    echo "$filepath"
}

# Function to update work log status
update_work_log_status() {
    local work_log="$1"
    local status="$2"
    
    if [[ ! -f "$work_log" ]]; then
        log_error "Work log not found: $work_log"
        return 1
    fi
    
    # Update status in the work log
    sed -i "s/\*\*Status\*\*: .*/\*\*Status\*\*: $status/" "$work_log"
    log_success "Updated work log status to: $status"
}

# Function to get git branch
get_git_branch() {
    git branch --show-current
}

# Function to check if we're on main branch
is_main_branch() {
    local branch=$(get_git_branch)
    [[ "$branch" == "main" || "$branch" == "master" ]]
}

# Function to ensure clean working directory
ensure_clean_working_dir() {
    if ! git diff-index --quiet HEAD --; then
        log_error "Working directory has uncommitted changes"
        git status --porcelain
        return 1
    fi
    
    if [[ -n "$(git diff --cached --name-only)" ]]; then
        log_error "Working directory has staged changes"
        git diff --cached --name-only
        return 1
    fi
    
    return 0
}

# Function to start work session
start_work_session() {
    log_info "Starting work session..."
    
    # Pull latest changes
    log_info "Pulling latest changes from remote..."
    if ! git pull origin $(get_git_branch); then
        log_error "Failed to pull changes. Please resolve conflicts manually."
        return 1
    fi
    
    # Ensure working directory is clean
    if ! ensure_clean_working_dir; then
        log_warning "Please commit or stash changes before starting new work"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return 1
        fi
    fi
    
    # Check for existing in-progress work logs
    local in_progress_logs=$(find "$WORK_LOGS_DIR" -name "*.md" -exec grep -l "Status.*In Progress" {} \;)
    if [[ -n "$in_progress_logs" ]]; then
        log_warning "Found existing in-progress work logs:"
        echo "$in_progress_logs"
        read -p "Continue with existing work or create new task? (continue/new): " -r
        if [[ $REPLY =~ ^[Cc]$ ]]; then
            echo "$in_progress_logs" | head -n1
            return 0
        fi
    fi
    
    # Create new work log
    local task_name=$(generate_task_name)
    local work_log=$(create_work_log "$task_name")
    echo "$work_log"
}

# Function to end work session
end_work_session() {
    log_info "Ending work session..."
    
    # Check for changes
    if ! git diff-index --quiet HEAD --; then
        log_info "Changes detected. Committing..."
        
        # Update work log status to completed
        local work_logs=$(find "$WORK_LOGS_DIR" -name "*.md" -exec grep -l "Status.*In Progress" {} \;)
        if [[ -n "$work_logs" ]]; then
            local latest_log=$(echo "$work_logs" | head -n1)
            update_work_log_status "$latest_log" "Completed"
            
            # Add work log changes to git
            git add "$latest_log"
        fi
        
        # Stage all changes
        git add -A
        
        # Commit with descriptive message
        local task_name=$(basename "${latest_log:-changes}" .md)
        git commit -m "$task_name: $(date +%Y-%m-%d) completion"
    fi
    
    # Push to remote
    log_info "Pushing changes to remote..."
    if ! git push origin $(get_git_branch); then
        log_error "Failed to push changes"
        return 1
    fi
    
    # Clean up completed work logs older than 7 days
    find "$WORK_LOGS_DIR" -name "*.md" -mtime +7 -exec rm {} \; 2>/dev/null || true
    
    log_success "Work session completed successfully"
}

# Function to switch to feature branch
switch_to_branch() {
    local branch_name="$1"
    
    if [[ -z "$branch_name" ]]; then
        log_error "Branch name required"
        echo "Usage: $0 branch <branch-name>"
        return 1
    fi
    
    # Check for uncommitted changes
    if ! ensure_clean_working_dir; then
        log_error "Cannot switch branches with uncommitted changes"
        return 1
    fi
    
    # Create and switch to branch
    if git show-branch "$branch_name" >/dev/null 2>&1; then
        log_info "Switching to existing branch: $branch_name"
        git checkout "$branch_name"
    else
        log_info "Creating and switching to new branch: $branch_name"
        git checkout -b "$branch_name"
    fi
    
    log_success "Switched to branch: $branch_name"
}

# Function to show help
show_help() {
    cat << EOF
Unified Development Workflow Script

Usage: $0 <command>

Commands:
    start       Start work session (pull changes, create work log)
    end         End work session (commit, push, update work log)
    branch <name> Switch to/create feature branch
    status      Show current git and work log status
    help        Show this help message

Examples:
    $0 start            # Start working (pull + create work log)
    $0 end              # Finish working (commit + push)
    $0 branch feature-x # Create/switch to feature branch
    $0 status           # Check current status

Workflow:
1. Run '$0 start' at beginning of work session
2. Work on your changes
3. Run '$0 end' when finished
4. Work logs are automatically created/updated

EOF
}

# Function to show status
show_status() {
    log_info "Current Git Status:"
    git status --short
    
    echo
    log_info "Current Branch: $(get_git_branch)"
    
    echo
    log_info "Recent Work Logs:"
    find "$WORK_LOGS_DIR" -name "*.md" -type f -exec basename {} \; | head -5
}

# Main script logic
case "${1:-}" in
    "start")
        start_work_session
        ;;
    "end")
        end_work_session
        ;;
    "branch")
        switch_to_branch "$2"
        ;;
    "status")
        show_status
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    "")
        log_error "Command required"
        show_help
        exit 1
        ;;
    *)
        log_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac