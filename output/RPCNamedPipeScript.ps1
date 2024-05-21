import-module ActiveDirectory
$username = 'myDomainUser'
$password = 'myDomainPassword'
$credential = New-Object System.Management.Automation.PSCredential -ArgumentList $username, (ConvertTo-SecureString -String $password -AsPlainText -Force)
$domainController = 'myDCName' 
$session = New-PSSession -ComputerName $domainController -Credential $credential 
Invoke-Command -Session $session { Test-Path "\.\pipe\myRpcPipe" }
