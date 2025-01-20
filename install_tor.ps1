# Download directory
$downloadDir = $PWD.Path
$torDir = Join-Path $downloadDir "tor"

# Create tor directory if it doesn't exist
if (-not (Test-Path $torDir)) {
    New-Item -ItemType Directory -Path $torDir | Out-Null
}

# Download Tor Expert Bundle
$torUrl = "https://archive.torproject.org/tor-package-archive/torbrowser/13.0.7/tor-expert-bundle-windows-x86_64-13.0.7.tar.gz"
$torArchive = Join-Path $downloadDir "tor-expert-bundle.tar.gz"

Write-Host "Downloading Tor Expert Bundle..."
Invoke-WebRequest -Uri $torUrl -OutFile $torArchive

# Extract the archive
Write-Host "Extracting Tor files..."
tar -xzf $torArchive -C $torDir

# Clean up the archive
Remove-Item $torArchive

Write-Host "Tor has been installed to: $torDir"
Write-Host "Adding Tor directory to PATH..."

# Add Tor directory to PATH for current session
$env:Path += ";$torDir\Tor"

Write-Host "Installation complete!"
