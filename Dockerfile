FROM python:3.10-slim

WORKDIR /app

# Copy project configuration and source code
COPY pyproject.toml ./
COPY src/ ./src/

# Install the package and its dependencies
RUN pip install --no-cache-dir .

# Run the MCP server
CMD ["davinci-resolve-mcp"]
