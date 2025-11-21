"""
MCP (Model Context Protocol) types and data structures.
"""

from typing import Dict, Any, List, Optional, Union, Literal
from dataclasses import dataclass, field
from enum import Enum


class McpVersion(str, Enum):
    V1_0 = "1.0"


@dataclass
class ToolCapability:
    tools: bool = True


@dataclass
class ResourceCapability:
    subscribe: Optional[bool] = None
    list_changed: Optional[bool] = None


@dataclass
class ServerCapabilities:
    tools: Optional[ToolCapability] = None
    resources: Optional[ResourceCapability] = None


@dataclass
class ClientCapabilities:
    tools: Optional[ToolCapability] = None
    resources: Optional[ResourceCapability] = None


@dataclass
class InitializeRequest:
    method: str = "initialize"
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InitializeResult:
    protocolVersion: str = McpVersion.V1_0
    capabilities: ServerCapabilities = field(default_factory=ServerCapabilities)
    serverInfo: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolParameter:
    type: str
    description: str
    required: Optional[bool] = False
    enum: Optional[List[str]] = None


@dataclass
class Tool:
    name: str
    description: str
    inputSchema: Dict[str, Any]


@dataclass
class ToolListResult:
    tools: List[Tool]


@dataclass
class ToolCallRequest:
    method: str = "tools/call"
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolResult:
    content: List[Dict[str, Any]]
    isError: bool = False


@dataclass
class McpRequest:
    jsonrpc: str = "2.0"
    id: Union[str, int] = ""
    method: str = ""
    params: Optional[Dict[str, Any]] = None


@dataclass
class McpResponse:
    jsonrpc: str = "2.0"
    id: Union[str, int] = ""
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


@dataclass
class McpError:
    code: int
    message: str
    data: Optional[Dict[str, Any]] = None


def dataclass_to_dict(obj):
    """Convert dataclass to dictionary."""
    if hasattr(obj, '__dataclass_fields__'):
        result = {}
        for field_name, field_def in obj.__dataclass_fields__.items():
            value = getattr(obj, field_name)
            if value is not None:
                if hasattr(value, '__dataclass_fields__'):
                    result[field_name] = dataclass_to_dict(value)
                elif isinstance(value, list):
                    result[field_name] = [dataclass_to_dict(item) if hasattr(item, '__dataclass_fields__') else item for item in value]
                else:
                    result[field_name] = value
        return result
    return obj

