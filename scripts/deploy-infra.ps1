param (
    [string]$StackName = "project-meety-dev",
    [string]$Region = "us-east-1",
    [string]$ArtifactBucket = "project-meety-artifacts-z0059cmc-us-east-1",
    [string]$InitialUsername = "adminuser",
    [string]$InitialUserEmail = "your-real-email@example.com",
    [string]$LexBotId = "WMP2CLWD5Y",
    [string]$LexBotAliasId = "TSTALIASID"
)

$ErrorActionPreference = "Stop"

$templatePath = Join-Path (Split-Path -Parent $PSScriptRoot) "infra\main.yaml"

aws cloudformation deploy `
  --template-file $templatePath `
  --stack-name $StackName `
  --capabilities CAPABILITY_NAMED_IAM `
  --region $Region `
  --parameter-overrides `
    ProjectName=project-meety `
    EnvironmentName=dev `
    InitialUsername=$InitialUsername `
    InitialUserEmail=$InitialUserEmail `
    LambdaArtifactBucket=$ArtifactBucket `
    LexBotId=$LexBotId `
    LexBotAliasId=$LexBotAliasId