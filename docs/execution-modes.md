# Execution Modes Guide

Bio-MCP servers support multiple execution modes to accommodate different computing environments, from personal workstations to academic clusters and cloud environments.

## Overview

The Bio-MCP servers can automatically detect and use bioinformatics tools from multiple sources:

1. **Native** - Tools installed directly on the system (in PATH)
2. **Module** - Tools available via Environment Modules
3. **Lmod** - Tools available via Lmod module system
4. **Singularity** - Tools available via Singularity containers
5. **Docker** - Tools available via Docker containers

## Automatic Detection

By default, Bio-MCP servers will automatically detect the best available execution mode in this order:

1. **Native** - Fastest execution, no overhead
2. **Module/Lmod** - Common on HPC clusters, optimized builds
3. **Singularity** - Good for clusters without root access
4. **Docker** - Good for development environments

## Configuration

### Environment Variables

Control execution behavior with these environment variables:

```bash
# Force a specific execution mode
export BIO_MCP_EXECUTION_MODE="module"

# Set preferred execution modes (comma-separated)
export BIO_MCP_PREFERRED_MODES="native,module,singularity,docker"

# Force container usage
export BIO_MCP_FORCE_CONTAINER="true"

# Specify module names to try
export BIO_MCP_MODULE_NAMES="blast,blast+,ncbi-blast+"

# Specify container image
export BIO_MCP_CONTAINER_IMAGE="biocontainers/blast:2.15.0"
```

### Configuration File

Create a `bio-mcp-config.yaml` file for more detailed configuration:

```yaml
# Global execution settings
execution:
  force_mode: null  # or: native, module, lmod, singularity, docker
  preferred_modes:
    - native
    - module
    - singularity
    - docker

# Module system settings
modules:
  tool_modules:
    blast: ["blast", "blast+", "ncbi-blast+"]
    samtools: ["samtools", "SAMtools"]
    bwa: ["bwa", "BWA"]

# Container settings
containers:
  singularity:
    images:
      blast: "biocontainers/blast:2.15.0"
  docker:
    images:
      blast: "biocontainers/blast:2.15.0"
```

## Execution Modes in Detail

### Native Mode

Tools are executed directly from the system PATH.

**Pros:**
- Fastest execution (no containerization overhead)
- Direct access to system resources
- Easy debugging

**Cons:**
- Requires manual tool installation
- Version management can be complex
- Platform-specific dependencies

**Example:**
```bash
# Tools must be in PATH
which blastn  # /usr/local/bin/blastn
```

### Module Mode (Environment Modules)

Tools are loaded via the Environment Modules system, common on HPC clusters.

**Pros:**
- Optimized builds for specific hardware
- Easy version management
- No container overhead
- Cluster-admin maintained

**Cons:**
- Requires module system setup
- Cluster-specific module names

**Example:**
```bash
# Check available modules
module avail blast

# MCP server will automatically run:
module load blast && blastn [arguments]
```

### Lmod Mode

Similar to Environment Modules but using the Lmod system.

**Pros:**
- Modern module system with dependency resolution
- Hierarchical module organization
- Better conflict resolution

**Cons:**
- Requires Lmod installation
- Learning curve for configuration

**Example:**
```bash
# Check available modules
ml avail blast

# MCP server will automatically run:
ml load blast && blastn [arguments]
```

### Singularity Mode

Tools are executed via Singularity containers.

**Pros:**
- No root access required
- Consistent environment across systems
- Good for HPC clusters
- Reproducible results

**Cons:**
- Container overhead
- Image management
- Potential I/O performance impact

**Example:**
```bash
# Build or pull container
singularity build blast.sif docker://biocontainers/blast:2.15.0

# MCP server will automatically run:
singularity exec blast.sif blastn [arguments]
```

### Docker Mode

Tools are executed via Docker containers.

**Pros:**
- Consistent environment
- Easy image management
- Good for development
- Reproducible results

**Cons:**
- Requires Docker daemon
- Root access typically needed
- Container overhead

**Example:**
```bash
# Pull container
docker pull biocontainers/blast:2.15.0

# MCP server will automatically run:
docker run --rm -v $PWD:/data biocontainers/blast:2.15.0 blastn [arguments]
```

## Common Use Cases

### Personal Workstation

```bash
# Use native tools if available, fallback to Docker
export BIO_MCP_PREFERRED_MODES="native,docker"
```

### University HPC Cluster

```bash
# Use modules first, fallback to Singularity
export BIO_MCP_PREFERRED_MODES="module,lmod,singularity"
export BIO_MCP_MODULE_NAMES="blast,BLAST,ncbi-blast+"
```

### Cloud Environment

```bash
# Use containers for consistency
export BIO_MCP_PREFERRED_MODES="docker,singularity"
export BIO_MCP_CONTAINER_IMAGE="biocontainers/blast:2.15.0"
```

### Development Environment

```bash
# Force container usage for reproducibility
export BIO_MCP_FORCE_CONTAINER="true"
export BIO_MCP_PREFERRED_MODES="docker,singularity"
```

## Tool-Specific Configuration

Configure execution modes for specific tools:

```bash
# Use modules for BLAST, native for other tools
export BIO_MCP_BLAST_EXECUTION_MODE="module"
export BIO_MCP_BLAST_MODULE_NAMES="blast,blast+"

# Use Singularity for InterProScan (long-running jobs)
export BIO_MCP_INTERPRO_EXECUTION_MODE="singularity"
export BIO_MCP_INTERPRO_CONTAINER_IMAGE="biocontainers/interproscan:5.63_95.0"
```

## Troubleshooting

### Check Tool Detection

Use the `blast_info` tool (available in enhanced servers) to see what was detected:

```python
# Via MCP client
result = await mcp_client.call_tool("blast_info", {})
print(result)
```

### Debug Detection Issues

Enable verbose logging:

```bash
export BIO_MCP_LOG_LEVEL="DEBUG"
export BIO_MCP_LOG_TOOL_DETECTION="true"
```

### Common Issues

1. **Module not found**: Check module names with `module avail` or `ml avail`
2. **Container not found**: Check image names and registry access
3. **Permission denied**: Check container runtime permissions
4. **Path issues**: Ensure tools are in PATH for native mode

## Performance Considerations

**Execution Speed (fastest to slowest):**
1. Native
2. Module/Lmod
3. Singularity
4. Docker

**Resource Usage:**
- Native: Minimal overhead
- Module: Minimal overhead
- Singularity: Low overhead
- Docker: Higher overhead

**I/O Performance:**
- Native: Best
- Module: Best
- Singularity: Good (with proper bind mounts)
- Docker: Good (with proper volume mounts)

## Security Considerations

- **Native**: Inherits system security
- **Module**: Inherits system security
- **Singularity**: User-level isolation
- **Docker**: Root-level isolation (typically)

Choose execution modes based on your security requirements and environment constraints.

## Migration Guide

### From Container-Only to Flexible Mode

1. **Set preferred modes**:
   ```bash
   export BIO_MCP_PREFERRED_MODES="native,module,singularity,docker"
   ```

2. **Keep container fallback**:
   ```bash
   export BIO_MCP_CONTAINER_IMAGE="your-current-image"
   ```

3. **Test detection**:
   ```bash
   # Check what's detected
   python -c "from src.tool_detection import ToolDetector; print(ToolDetector().detect_tool('blastn'))"
   ```

### From Native-Only to Flexible Mode

1. **Add container fallback**:
   ```bash
   export BIO_MCP_PREFERRED_MODES="native,docker"
   export BIO_MCP_CONTAINER_IMAGE="biocontainers/blast:2.15.0"
   ```

2. **Test with missing tools**:
   ```bash
   # Temporarily rename tool to test fallback
   sudo mv /usr/bin/blastn /usr/bin/blastn.backup
   # Test MCP server - should use container
   sudo mv /usr/bin/blastn.backup /usr/bin/blastn
   ```

This flexible execution mode system ensures your Bio-MCP servers work across different environments while maintaining optimal performance and user control.