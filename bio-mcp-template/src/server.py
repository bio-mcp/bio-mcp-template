import asyncio
import logging
import os
import tempfile
from pathlib import Path
from typing import Any, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, ErrorContent
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

from .tool_detection import ToolDetector, ToolConfig, ExecutionMode, ToolInfo


logger = logging.getLogger(__name__)


class ServerSettings(BaseSettings):
    max_file_size: int = Field(default=100_000_000, description="Maximum input file size in bytes")
    temp_dir: Optional[str] = Field(default=None, description="Temporary directory for processing")
    timeout: int = Field(default=300, description="Command timeout in seconds")
    {{tool_name}}_path: str = Field(default="{{tool_name}}", description="Path to {{tool_name}} executable")
    
    # Tool execution mode settings
    execution_mode: Optional[str] = Field(default=None, description="Force specific execution mode (native, module, lmod, singularity, docker)")
    preferred_modes: str = Field(default="native,module,lmod,singularity,docker", description="Preferred execution modes in order")
    
    # Module settings
    module_names: str = Field(default="{{tool_name}}", description="Comma-separated list of module names to try")
    
    # Container settings
    container_image: str = Field(default="biocontainers/{{tool_name}}:{{tool_version}}", description="Container image for {{tool_name}}")
    singularity_image_path: Optional[str] = Field(default=None, description="Path to Singularity image")
    
    class Config:
        env_prefix = "BIO_MCP_"


class {{ToolName}}Server:
    def __init__(self, settings: Optional[ServerSettings] = None):
        self.settings = settings or ServerSettings()
        self.server = Server("bio-mcp-{{tool_name}}")
        self.detector = ToolDetector(logger)
        self.tool_config = ToolConfig.from_env()
        self.tool_info = None
        self._setup_handlers()
        
    async def _detect_tool(self) -> ToolInfo:
        """Detect the best available execution mode for {{tool_name}}."""
        if self.tool_info is not None:
            return self.tool_info
        
        # Parse settings
        force_mode = None
        if self.settings.execution_mode:
            try:
                force_mode = ExecutionMode(self.settings.execution_mode.lower())
            except ValueError:
                logger.warning(f"Invalid execution mode: {self.settings.execution_mode}")
        
        preferred_modes = []
        for mode_str in self.settings.preferred_modes.split(","):
            try:
                mode = ExecutionMode(mode_str.strip().lower())
                preferred_modes.append(mode)
            except ValueError:
                logger.warning(f"Invalid preferred mode: {mode_str}")
        
        module_names = [name.strip() for name in self.settings.module_names.split(",")]
        
        # Detect tool
        self.tool_info = self.detector.detect_tool(
            tool_name="{{tool_name}}",
            module_names=module_names,
            container_image=self.settings.container_image,
            preferred_modes=preferred_modes or None,
            force_mode=force_mode
        )
        
        return self.tool_info
        
    def _setup_handlers(self):
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [
                Tool(
                    name="{{tool_name}}_run",
                    description="{{tool_main_description}}",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "input_file": {
                                "type": "string", 
                                "description": "Path to input file"
                            },
                            # Add tool-specific parameters here
                            "{{param_name}}": {
                                "type": "{{param_type}}",
                                "description": "{{param_description}}"
                            },
                        },
                        "required": ["input_file"]
                    }
                ),
                # Add more tool functions as needed
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent | ImageContent | ErrorContent]:
            if name == "{{tool_name}}_run":
                return await self._run_{{tool_name}}(arguments)
            else:
                return [ErrorContent(text=f"Unknown tool: {name}")]
    
    async def _run_{{tool_name}}(self, arguments: dict) -> list[TextContent | ErrorContent]:
        try:
            # Validate input file
            input_path = Path(arguments["input_file"])
            if not input_path.exists():
                return [ErrorContent(text=f"Input file not found: {input_path}")]
            
            if input_path.stat().st_size > self.settings.max_file_size:
                return [ErrorContent(text=f"File too large. Maximum size: {self.settings.max_file_size} bytes")]
            
            # Create temporary directory for processing
            with tempfile.TemporaryDirectory(dir=self.settings.temp_dir) as tmpdir:
                # Copy input file to temp directory
                temp_input = Path(tmpdir) / input_path.name
                temp_input.write_bytes(input_path.read_bytes())
                
                # Detect tool and build command
                tool_info = await self._detect_tool()
                
                if tool_info.mode == ExecutionMode.UNAVAILABLE:
                    return [ErrorContent(text="{{tool_name}} is not available in any execution mode")]
                
                # Build command arguments
                tool_args = [
                    # Add tool-specific arguments here
                    str(temp_input)
                ]
                
                # Get the complete command based on execution mode
                cmd = self.detector.get_execution_command(tool_info, tool_args)
                
                logger.info(f"Executing {{tool_name}} via {tool_info.mode.value}: {' '.join(cmd)}")
                
                # Execute command
                # For module-based execution, we need to handle shell commands
                if tool_info.mode in [ExecutionMode.MODULE, ExecutionMode.LMOD]:
                    # Module commands need to be executed in shell
                    shell_cmd = " ".join(cmd)
                    process = await asyncio.create_subprocess_shell(
                        shell_cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        cwd=tmpdir
                    )
                else:
                    # Direct execution for native, container modes
                    process = await asyncio.create_subprocess_exec(
                        *cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        cwd=tmpdir
                    )
                
                try:
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(),
                        timeout=self.settings.timeout
                    )
                except asyncio.TimeoutError:
                    process.kill()
                    return [ErrorContent(text=f"Command timed out after {self.settings.timeout} seconds")]
                
                if process.returncode != 0:
                    return [ErrorContent(text=f"Command failed: {stderr.decode()}"
                )]
                
                # Process output
                output = stdout.decode()
                
                # Return results
                return [TextContent(text=output)]
                
        except Exception as e:
            logger.error(f"Error running {{tool_name}}: {e}", exc_info=True)
            return [ErrorContent(text=f"Error: {str(e)}")]
    
    async def run(self):
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream)


async def main():
    logging.basicConfig(level=logging.INFO)
    server = {{ToolName}}Server()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())