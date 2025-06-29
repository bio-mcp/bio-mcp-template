# Bio-MCP Template

🧬 **Template repository for creating new bioinformatics MCP servers**

Use this template to quickly create MCP servers for new bioinformatics tools. This template provides a complete, production-ready foundation with best practices built-in.

## 🚀 Quick Start

### 1. Use This Template

Click "Use this template" on GitHub or:

```bash
gh repo create your-org/bio-mcp-newtool --template bio-mcp/bio-mcp-template
cd bio-mcp-newtool
```

### 2. Customize for Your Tool

```bash
# Replace placeholders in files
find . -type f -name "*.py" -o -name "*.md" -o -name "*.toml" | xargs sed -i 's/{{tool_name}}/newtool/g'
find . -type f -name "*.py" -o -name "*.md" -o -name "*.toml" | xargs sed -i 's/{{ToolName}}/NewTool/g'
find . -type f -name "*.py" -o -name "*.md" -o -name "*.toml" | xargs sed -i 's/{{tool_description}}/My new bioinformatics tool/g'
```

### 3. Implement Your Tool

Edit `src/server.py` and add your tool's functions following the provided patterns.

### 4. Test and Deploy

```bash
pip install -e .[dev]
pytest tests/
python -m src.server
```

## 📋 What's Included

### Core Infrastructure
- ✅ **Complete MCP server** implementation
- ✅ **Error handling** and input validation
- ✅ **Configuration management** via environment variables
- ✅ **Logging** and monitoring setup
- ✅ **Docker support** with biocontainers integration

### Testing & Quality
- ✅ **Test framework** with pytest
- ✅ **Code formatting** with ruff
- ✅ **CI/CD workflows** for GitHub Actions
- ✅ **Type hints** and documentation

### Deployment
- ✅ **Docker containerization** 
- ✅ **Queue system integration** for async jobs
- ✅ **Kubernetes manifests**
- ✅ **Cloud deployment** configurations

### Documentation
- ✅ **README template** with examples
- ✅ **API documentation** structure
- ✅ **Contributing guidelines**
- ✅ **Security considerations**

## 🛠️ Customization Guide

### 1. Tool Configuration

Edit `pyproject.toml`:
```toml
[project]
name = "bio-mcp-yourtool"
description = "MCP server for YourTool bioinformatics software"
```

### 2. Server Implementation

Edit `src/server.py` and implement these methods:

```python
@self.server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="yourtool_function",
            description="What this function does",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_file": {"type": "string", "description": "Input file"},
                    # Add your parameters
                },
                "required": ["input_file"]
            }
        )
    ]

async def _run_yourtool_function(self, arguments: dict):
    # Implement your tool execution here
    pass
```

### 3. Docker Configuration

Edit `Dockerfile`:
```dockerfile
# Change the base image to include your tool
FROM biocontainers/yourtool:latest AS tool

# Copy your tool binaries
COPY --from=tool /usr/local/bin/yourtool /usr/local/bin/
```

### 4. Tests

Edit `tests/test_server.py`:
```python
@pytest.mark.asyncio
async def test_yourtool_function():
    server = YourToolServer()
    result = await server._run_yourtool_function({"input_file": "test.txt"})
    assert len(result) == 1
    # Add your assertions
```

## 📦 Template Structure

```
bio-mcp-template/
├── src/
│   ├── server.py              # Main MCP server implementation
│   ├── queue_integration.py   # Optional queue support
│   └── config.yaml           # Configuration template
├── tests/
│   └── test_server.py        # Test suite
├── examples/
│   └── example_usage.py      # Usage examples
├── Dockerfile                # Container definition
├── pyproject.toml           # Python project configuration
├── README.md                # Documentation template
└── .github/
    └── workflows/
        └── test.yml         # CI/CD pipeline
```

## 🧬 Implementation Patterns

### Input Validation
```python
async def _run_tool(self, arguments: dict):
    input_file = Path(arguments["input_file"])
    if not input_file.exists():
        return [ErrorContent(text=f"Input file not found: {input_file}")]
    
    if input_file.stat().st_size > self.settings.max_file_size:
        return [ErrorContent(text=f"File too large")]
```

### Command Execution
```python
with tempfile.TemporaryDirectory(dir=self.settings.temp_dir) as tmpdir:
    cmd = [self.settings.tool_path, "--input", str(input_file)]
    
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, stderr = await asyncio.wait_for(
        process.communicate(),
        timeout=self.settings.timeout
    )
```

### Error Handling
```python
try:
    # Tool execution
    pass
except subprocess.TimeoutExpired:
    return [ErrorContent(text="Tool execution timed out")]
except subprocess.CalledProcessError as e:
    return [ErrorContent(text=f"Tool failed: {e.stderr.decode()}")]
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    return [ErrorContent(text=f"Error: {str(e)}")]
```

## 🔧 Advanced Features

### Queue Integration

Add async job support:
```python
from queue_integration import QueueIntegrationMixin

class YourToolServerWithQueue(QueueIntegrationMixin, YourToolServer):
    def __init__(self, settings=None, queue_url=None):
        self.queue_url = queue_url or "http://localhost:8000"
        super().__init__(settings)
        self._setup_async_handlers()
```

### Multiple Output Formats

Support different output formats:
```python
output_formats = {
    "json": self._format_as_json,
    "csv": self._format_as_csv,
    "text": self._format_as_text
}

formatter = output_formats.get(arguments.get("output_format", "text"))
formatted_output = formatter(raw_result)
```

### Progress Tracking

For long-running operations:
```python
async def _run_long_operation(self, arguments: dict):
    total_steps = 100
    for i in range(total_steps):
        # Do work
        progress = (i + 1) / total_steps * 100
        logger.info(f"Progress: {progress:.1f}%")
        await asyncio.sleep(0.1)  # Yield control
```

## 📚 Best Practices

### Scientific Accuracy
- Use the tool's native parameter names
- Preserve biological meaning in error messages
- Handle edge cases in biological data
- Follow field conventions for file formats

### Performance
- Set appropriate timeout values for your tool
- Consider memory usage for large datasets
- Use streaming for very large files
- Implement progress reporting for long operations

### Security
- Validate all input parameters
- Sanitize file paths
- Use secure temporary directories
- Clean up temporary files

### Maintainability
- Follow consistent coding patterns
- Add comprehensive error handling
- Include meaningful log messages
- Write clear documentation

## 🤝 Contributing

1. **Fork this template** repository
2. **Make improvements** to the template itself
3. **Submit a pull request** with your enhancements
4. **Help others** by reviewing template usage

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

## 🆘 Support

- 📖 **Documentation**: [Bio-MCP Docs](https://github.com/bio-mcp/bio-mcp-docs)
- 🐛 **Issues**: [Report bugs](https://github.com/bio-mcp/bio-mcp-template/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/bio-mcp/bio-mcp-template/discussions)
- 💡 **Examples**: [Bio-MCP Examples](https://github.com/bio-mcp/bio-mcp-examples)

---

**Happy coding! 🧬✨**