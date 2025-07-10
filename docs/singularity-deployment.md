# Singularity Deployment Guide

This guide explains how to deploy Bio-MCP servers using Singularity containers, which is particularly useful for academic clusters and HPC environments where Docker may not be available.

## Prerequisites

- Singularity/Apptainer installed on your system
- Access to build containers (may require `sudo` or `--fakeroot`)
- Python 3.9+ for MCP client integration

## Building Singularity Images

Each Bio-MCP server includes a `Singularity.def` definition file. To build a Singularity image:

```bash
cd bio-mcp-blast  # or any other bio-mcp-* directory
sudo singularity build blast.sif Singularity.def
```

For systems without root access, use fakeroot:

```bash
singularity build --fakeroot blast.sif Singularity.def
```

## Running MCP Servers

### Direct Execution

Run the MCP server directly:

```bash
singularity run blast.sif
```

### With Custom Environment Variables

```bash
singularity run --env BIO_MCP_TIMEOUT=600 --env BIO_MCP_MAX_FILE_SIZE=5000000000 blast.sif
```

### With Bind Mounts

For processing files on the host system:

```bash
singularity run --bind /path/to/data:/data blast.sif
```

## Integration with Claude Desktop

Add to your `claude_desktop_config.json`:

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

## Available Tools

All Bio-MCP servers have corresponding Singularity definition files:

- `bio-mcp-blast/Singularity.def` - BLAST sequence analysis
- `bio-mcp-samtools/Singularity.def` - SAM/BAM file operations
- `bio-mcp-fastqc/Singularity.def` - Quality control analysis
- `bio-mcp-bedtools/Singularity.def` - Genomic interval operations
- `bio-mcp-bwa/Singularity.def` - Sequence alignment
- `bio-mcp-seqkit/Singularity.def` - Sequence manipulation
- `bio-mcp-bcftools/Singularity.def` - Variant calling utilities
- `bio-mcp-interpro/Singularity.def` - Protein domain analysis
- `bio-mcp-amber/Singularity.def` - Molecular dynamics simulations

## Environment Variables

Each server supports these common environment variables:

- `BIO_MCP_TEMP_DIR`: Temporary directory for processing (default: `/tmp/mcp-work`)
- `BIO_MCP_TIMEOUT`: Command timeout in seconds (varies by tool)
- `BIO_MCP_MAX_FILE_SIZE`: Maximum input file size in bytes
- `BIO_MCP_<TOOL>_PATH`: Path to specific tool binary

## HPC/SLURM Integration

For SLURM clusters, create a wrapper script:

```bash
#!/bin/bash
#SBATCH --job-name=bio-mcp-blast
#SBATCH --time=01:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G

module load singularity

singularity run --bind $SCRATCH:/data /path/to/blast.sif
```

## Troubleshooting

### Build Issues

1. **Permission denied**: Use `--fakeroot` or build with `sudo`
2. **Network issues**: Some clusters may need `--network=none` during build
3. **Disk space**: Ensure adequate space in `/tmp` and build directory

### Runtime Issues

1. **File not found**: Check bind mounts with `--bind`
2. **Permission errors**: Verify file permissions and ownership
3. **Tool not found**: Check that the base biocontainer includes the tool

### Testing Your Build

Each Singularity definition includes a `%test` section:

```bash
singularity test blast.sif
```

This verifies that the bioinformatics tools and Python environment are properly configured.

## Performance Considerations

- Use `--bind` to mount data directories for better I/O performance
- Consider `--writable-tmpfs` for temporary file operations
- Use `--cpu-bind` and `--memory-bind` for NUMA-aware execution on HPC systems

## Security

Singularity containers run with user privileges by default, making them suitable for multi-user environments. No additional security configuration is typically needed.

## Container Registry

For shared environments, consider hosting built images on a registry:

```bash
# Build and push to registry
singularity build blast.sif Singularity.def
singularity push blast.sif library://your-namespace/bio-mcp/blast:latest

# Pull from registry
singularity pull library://your-namespace/bio-mcp/blast:latest
```