param (
    [string]$ArtifactBucket = "project-meety-artifacts-z0059cmc-us-east-1"
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$buildDir = Join-Path $root "build"

if (Test-Path $buildDir) {
    Remove-Item $buildDir -Recurse -Force
}

New-Item -ItemType Directory -Path $buildDir | Out-Null

$lambdas = @(
    "chatbot-api",
    "get-meetings",
    "get-pending-meetings",
    "lex-fulfillment",
    "update-meeting-status"
)

foreach ($lambda in $lambdas) {
    $sourcePath = Join-Path $root "backend\$lambda"
    $tempPath = Join-Path $buildDir $lambda
    $zipPath = Join-Path $buildDir "$lambda.zip"

    Copy-Item $sourcePath $tempPath -Recurse
    Copy-Item (Join-Path $root "backend\shared") (Join-Path $tempPath "shared") -Recurse

    Compress-Archive -Path "$tempPath\*" -DestinationPath $zipPath -Force

    aws s3 cp $zipPath "s3://$ArtifactBucket/$lambda.zip"
}

Write-Host "Lambda packaging complete."