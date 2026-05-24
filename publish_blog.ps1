$sourceDir = "D:\Obsidian Vault\Attachments"
$destDir = "$PSScriptRoot\assets\images\posts"

Write-Host "Starting auto-publish script..." -ForegroundColor Cyan

# Create destination directory if it doesn't exist
if (!(Test-Path -Path $destDir)) {
    New-Item -ItemType Directory -Path $destDir | Out-Null
}

# Scan all markdown files in _posts and Myblog
$markdownFiles = Get-ChildItem -Path "$PSScriptRoot\_posts", "$PSScriptRoot\Myblog" -Filter "*.md" -Recurse -ErrorAction SilentlyContinue

foreach ($file in $markdownFiles) {
    # Use .NET to read as UTF-8
    $content = [System.IO.File]::ReadAllText($file.FullName, [System.Text.Encoding]::UTF8)
    $originalContent = $content
    
    # --- 1. Find and process standard Markdown links pointing to Attachments ---
    # Example: ![](../../Attachments/Pasted%20image%20123.png)
    $regex = '!\[(.*?)\]\((?:.*?Attachments/)(.*?)\)'
    $matches = [regex]::Matches($content, $regex)
    foreach ($match in $matches) {
        $filename = [uri]::UnescapeDataString($match.Groups[2].Value)
        $sourcePath = Join-Path -Path $sourceDir -ChildPath $filename
        $destPath = Join-Path -Path $destDir -ChildPath $filename
        
        if (Test-Path -Path $sourcePath) {
            Copy-Item -Path $sourcePath -Destination $destPath -Force
        } else {
            Write-Host "Warning: Could not find image $filename in D:\Obsidian Vault\Attachments" -ForegroundColor Yellow
        }
    }
    
    # Replace standard links in content
    $content = [regex]::Replace($content, $regex, {
        param($m)
        $alt = $m.Groups[1].Value
        $filename = $m.Groups[2].Value
        return "![${alt}](/assets/images/posts/${filename})"
    })

    # --- 2. Find and process Wikilinks ---
    # Example: ![[Pasted image 123.png]]
    $wikiRegex = '!\[\[(.*?)\]\]'
    $wikiMatches = [regex]::Matches($content, $wikiRegex)
    foreach ($match in $wikiMatches) {
        $filename = $match.Groups[1].Value
        $sourcePath = Join-Path -Path $sourceDir -ChildPath $filename
        $destPath = Join-Path -Path $destDir -ChildPath $filename
        
        if (Test-Path -Path $sourcePath) {
            Copy-Item -Path $sourcePath -Destination $destPath -Force
        } else {
            Write-Host "Warning: Could not find image $filename in D:\Obsidian Vault\Attachments" -ForegroundColor Yellow
        }
    }
    
    # Replace Wikilinks in content
    $content = [regex]::Replace($content, $wikiRegex, {
        param($m)
        $filename = $m.Groups[1].Value
        $uriFilename = [uri]::EscapeDataString($filename)
        return "![img](/assets/images/posts/${uriFilename})"
    })

    # Save file if changes were made
    if ($content -cne $originalContent) {
        # Use .NET to write UTF-8 without BOM
        $utf8NoBom = New-Object System.Text.UTF8Encoding $False
        [System.IO.File]::WriteAllText($file.FullName, $content, $utf8NoBom)
        Write-Host "Updated links in $($file.Name)" -ForegroundColor Green
    }
}

Write-Host "Processing Git commands..." -ForegroundColor Cyan
Set-Location -Path $PSScriptRoot

# Git Add
Write-Host "git add ."
git add .

# Git Commit
Write-Host 'git commit -m "Auto-publish: Add new posts and attachments"'
git commit -m "Auto-publish: Add new posts and attachments"

# Git Push
Write-Host "git push"
git push

Write-Host "All done! Your blog is updated." -ForegroundColor Green
# Write-Host "Press any key to exit..."
# $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") | Out-Null
