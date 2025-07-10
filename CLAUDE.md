# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Architecture

Bio-MCP is a collection of Model Context Protocol (MCP) servers that enable AI assistants to execute bioinformatics tools. The project uses a modular architecture where each bioinformatics tool gets its own MCP server implementation.

### Core Structure
- **Individual MCP servers**: `bio-mcp-blast/`, `bio-mcp-samtools/`, `bio-mcp-bwa/`, `bio-mcp-seqkit/`, etc.
- **Template system**: `bio-mcp-template/` provides boilerplate for new tools
- **Queue system**: `bio-mcp-queue/` handles async processing for long-running jobs
- **Deployment configs**: `deployment/` contains Kubernetes, AWS ECS, and Railway configurations

### Execution Modes

#### Processing Modes
- **Immediate mode**: Direct tool execution for quick jobs (< 5 minutes)
- **Queue mode**: Background processing using Celery + Redis + MinIO for large datasets
- Tools can support both modes, with automatic selection based on job size

#### Tool Execution Modes
Bio-MCP servers support intelligent tool detection across multiple environments:
- **Native**: Tools available in system PATH (fastest)
- **Module**: Tools available via Environment Modules (common on HPC)
- **Lmod**: Tools available via Lmod module system
- **Singularity**: Tools available via Singularity containers (HPC-friendly)
- **Docker**: Tools available via Docker containers (development-friendly)

Servers automatically detect and use the best available execution mode, with user-configurable preferences.

## Common Development Commands

### Individual MCP Server Development
```bash
# Set up a specific server for development
cd bio-mcp-blast  # or any other bio-mcp-* directory
pip install -e .[dev]

# Run tests
pytest tests/ -v

# Start server directly
python -m src.server

# Run with queue support
python -m src.main --mode queue

# Run with enhanced execution mode detection
python -m src.server_enhanced
```

### Execution Mode Configuration
```bash
# Force specific execution mode
export BIO_MCP_EXECUTION_MODE="module"  # or: native, lmod, singularity, docker

# Set preferred modes in order
export BIO_MCP_PREFERRED_MODES="native,module,singularity,docker"

# Tool-specific module names
export BIO_MCP_MODULE_NAMES="blast,blast+,ncbi-blast+"

# Container image for fallback
export BIO_MCP_CONTAINER_IMAGE="biocontainers/blast:2.15.0"

# Force container usage
export BIO_MCP_FORCE_CONTAINER="true"
```

### Testing
```bash
# Run tests for a specific server
cd bio-mcp-blast
pytest tests/ -v

# Lint and format code
ruff check .
ruff format .
```

### Queue System
```bash
# Start complete local queue system
cd bio-mcp-queue
./setup-local.sh

# Access monitoring dashboards
# - Job Queue: http://localhost:5555
# - File Storage: http://localhost:9001  
# - API Docs: http://localhost:8000/docs
```

### Docker Development
```bash
# Start all services locally
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Start production-like environment
docker-compose up -d
```

### Singularity Development
```bash
# Build Singularity image for a specific server
cd bio-mcp-blast
sudo singularity build blast.sif Singularity.def

# Or without root using fakeroot
singularity build --fakeroot blast.sif Singularity.def

# Run the server
singularity run blast.sif

# Test the build
singularity test blast.sif
```

## Development Patterns

### MCP Server Structure
Each bio-mcp-* server follows this pattern:
- `src/server.py`: Main MCP server implementation with tool definitions
- `src/server_enhanced.py`: Enhanced server with intelligent tool detection (where available)
- `src/server_with_queue.py`: Queue-enabled version (if applicable)
- `src/tool_detection.py`: Tool detection utility for multiple execution modes
- `tests/test_server.py`: Unit tests using pytest
- `pyproject.toml`: Python packaging with standardized dependencies
- `Dockerfile`: Containerization using biocontainers base images
- `Singularity.def`: Singularity definition for HPC/academic cluster deployment
- `bio-mcp-config.yaml`: Configuration file for execution mode preferences

### Dependencies
All servers use consistent core dependencies:
- `mcp>=1.1.0`: MCP protocol implementation
- `pydantic>=2.0.0`: Data validation and settings
- Development dependencies include `pytest`, `pytest-asyncio`, and `ruff`

### Error Handling
Servers implement comprehensive error handling:
- Input file validation and existence checks
- File size limits (configurable via environment variables)
- Clear error messages returned as MCP ErrorContent
- Temporary file cleanup

### Template Usage
When creating new tools:
1. Copy `bio-mcp-template/` to `bio-mcp-newtool/`
2. Replace template placeholders ({{tool_name}}, {{ToolName}}, etc.)
3. Implement tool-specific functions in `src/server.py`
4. Add appropriate tests following existing patterns
5. Update Docker configuration if needed

## Configuration

### Environment Variables
- `BIO_MCP_TIMEOUT`: Command timeout in seconds (default varies by tool)
- `BIO_MCP_MAX_FILE_SIZE`: Maximum input file size in bytes
- `BIO_QUEUE_WORKER_CONCURRENCY`: Number of parallel workers for queue mode
- Tool-specific paths can be configured via `{TOOL}_PATH` variables

### Claude Desktop Integration

#### Docker Integration
Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "bio-blast": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/bio-mcp-blast"
    }
  }
}
```

#### Singularity Integration
For HPC/academic clusters using Singularity:
```json
{
  "mcpServers": {
    "bio-blast": {
      "command": "singularity",
      "args": ["run", "/path/to/blast.sif"],
      "env": {
        "BIO_MCP_TIMEOUT": "600",
        "BIO_MCP_MAX_FILE_SIZE": "5000000000"
      }
    }
  }
}
```

## Security & Best Practices

- All user inputs are validated before execution
- Temporary directories are used for processing and cleaned up automatically
- File size limits prevent resource exhaustion
- No sensitive data is logged
- Docker containers provide isolation for tool execution
- Input files are checked for existence and permissions before processing