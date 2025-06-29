# Use biocontainers base image with {{tool_name}}
FROM biocontainers/{{tool_name}}:{{tool_version}} AS tool

# Build MCP server layer
FROM python:3.11-slim

# Copy {{tool_name}} from biocontainer
COPY --from=tool /usr/local/bin/{{tool_name}} /usr/local/bin/
# Copy any required libraries/dependencies
# COPY --from=tool /usr/local/lib/ /usr/local/lib/

# Install Python dependencies
WORKDIR /app
COPY pyproject.toml .
RUN pip install -e .

# Copy server code
COPY src/ ./src/

# Create non-root user
RUN useradd -m -u 1000 mcp && \
    mkdir -p /tmp/mcp-work && \
    chown -R mcp:mcp /app /tmp/mcp-work

USER mcp

# Set environment variables
ENV BIO_MCP_TEMP_DIR=/tmp/mcp-work
ENV BIO_MCP_{{TOOL_NAME}}_PATH=/usr/local/bin/{{tool_name}}

# Run the server
CMD ["python", "-m", "src.server"]