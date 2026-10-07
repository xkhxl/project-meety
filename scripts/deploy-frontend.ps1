param (
    [string]$StackName = "project-meety-dev",
    [string]$Region = "us-east-1"
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$frontendPath = Join-Path $projectRoot "frontend"

$bucketName = aws cloudformation describe-stacks `
  --stack-name $StackName `
  --region $Region `
  --query "Stacks[0].Outputs[?OutputKey=='FrontendBucketName'].OutputValue" `
  --output text

if (-not $bucketName) {
    throw "Could not find FrontendBucketName in stack outputs."
}

Write-Host "Using frontend bucket: $bucketName"

Push-Location $frontendPath
npm run build
aws s3 sync .\dist "s3://$bucketName" --delete
Pop-Location

Write-Host "Frontend deployed successfully."