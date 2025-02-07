# Load environment variables from .env file
include .env
export

# Variables for AWS CodeArtifact URL construction
CODEARTIFACT_URL = https://aws:$${UV_INDEX_SIGNATURE_PASSWORD}@${CODEARTIFACT_DOMAIN}-${AWS_ACCOUNT_ID}.d.codeartifact.${AWS_REGION}.amazonaws.com/pypi/${CODEARTIFACT_REPO}/simple/

.PHONY: token setup

# Generate AWS CodeArtifact token silently
token:
	@$(eval UV_INDEX_SIGNATURE_PASSWORD := $(shell aws codeartifact get-authorization-token \
		--domain ${CODEARTIFACT_DOMAIN} \
		--domain-owner ${AWS_ACCOUNT_ID} \
		--query authorizationToken \
		--output text))
	@echo "Token generated successfully"

# Setup environment with dependencies
setup: token
	@UV_INDEX_SIGNATURE_PASSWORD=${UV_INDEX_SIGNATURE_PASSWORD} UV_EXTRA_INDEX_URL=${CODEARTIFACT_URL} uv sync