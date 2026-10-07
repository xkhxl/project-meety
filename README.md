# Project Meety

A production-style reimplementation of a serverless meeting scheduler built on AWS using CloudFormation only.

## Features

- Cognito authentication
- Amazon Lex chatbot for meeting booking
- Lambda-based backend APIs
- DynamoDB for meeting storage
- Admin approval workflow
- Calendar view for approved meetings
- Frontend hosted with S3 + CloudFront

## Architecture

- Frontend: React + TypeScript + Vite
- Auth: Amazon Cognito
- API: API Gateway HTTP API
- Compute: AWS Lambda
- Database: DynamoDB
- Chatbot: Amazon Lex V2
- Hosting: S3 + CloudFront
- IaC: AWS CloudFormation

## Current status

Working end-to-end:

- login
- chatbot booking
- DynamoDB persistence
- pending meetings
- approve/reject flow
- approved meetings in calendar

## Hosted URL

- https://d1fw64xb4pjvq4.cloudfront.net

## Deployment

1. Package Lambda functions
2. Deploy CloudFormation stack
3. Build and deploy frontend
4. Open CloudFront URL

## Notes

This project was rebuilt from a course project into a cleaner, more portfolio-ready implementation with separated Lambda code, improved API response handling, and a reproducible infrastructure flow.
