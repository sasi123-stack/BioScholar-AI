# Deploy to Hugging Face Spaces Script

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   Deploy Backend to Hugging Face Spaces" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check if git is installed
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Git is not installed or not in PATH." -ForegroundColor Red
    exit 1
}

# 1. Ask for Space Name/URL
$spaceUrl = Read-Host "Enter your Hugging Face Space URL (e.g., https://huggingface.co/spaces/USERNAME/SPACE_NAME)"

if (-not $spaceUrl) {
    Write-Host "Error: Space URL is required." -ForegroundColor Red
    exit 1
}

# 2. Add Remote
Write-Host "`nConfiguring Git Remote..." -ForegroundColor Yellow
# Remove existing 'space' remote if it exists to avoid errors on re-run
git remote remove space 2>$null

try {
    git remote add space $spaceUrl
    Write-Host "Remote 'space' added successfully." -ForegroundColor Green
}
catch {
    Write-Host "Failed to add remote. Check if it already exists or URL is valid." -ForegroundColor Red
    exit 1
}

# 3. Push to Space
Write-Host "`nPushing to Hugging Face Spaces..." -ForegroundColor Yellow
Write-Host "This might take a while for large repositories." -ForegroundColor Gray
Write-Host "You may be prompted for your Hugging Face credentials." -ForegroundColor Magenta

# Check current branch name
$branch = git branch --show-current
if (-not $branch) {
    $branch = "master" # Fallback
}

try {
    # Force push to main on the space remote
    git push space $branch`:main --force
    Write-Host "`nCode pushed successfully!" -ForegroundColor Green
    Write-Host "Build has started on Hugging Face." -ForegroundColor Green
    Write-Host "Check the 'Build' tab on your Space page for progress." -ForegroundColor Cyan
}
catch {
    Write-Host "`nPush failed." -ForegroundColor Red
    Write-Host "Common reasons:" -ForegroundColor Yellow
    Write-Host "1. Authentication failed (Check your HF token)"
    Write-Host "2. Internet connection issues"
    Write-Host "3. Large files (>10MB) without LFS (Keep models out of repo)"
}
