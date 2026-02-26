# Repository Analysis Tools (`ra_tools`)

This directory contains MCP (Model Context Protocol) integration tools that extend the Repository Analysis framework with external service capabilities.

## Overview

The `ra_tools` package provides:
- **Runtime validation** for MCP server availability
- **Graceful degradation** when MCP servers are unavailable
- **Safety enforcement** for read-only vs write operations
- **Configuration helpers** for Claude Agent SDK integration

## Available Integrations

### 1. Pulumi MCP Integration ✅

**Purpose**: Read-only access to Pulumi-managed cloud infrastructure for architecture documentation.

**Status**: Production-ready (Phase 2 complete)

**Module**: [pulumi_integration.py](pulumi_integration.py)

**Safety Level**: READ-ONLY (strictly enforced)

#### Allowed Tools

The following Pulumi MCP tools are whitelisted for read-only operations:

- `mcp__pulumi__get-stacks` - List all Pulumi stacks
- `mcp__pulumi__resource-search` - Search cloud resources using Lucene queries
- `mcp__pulumi__get-policy-violations` - Check compliance status
- `mcp__pulumi__get-users` - List organization members
- `mcp__pulumi__neo-get-tasks` - List Neo task history (read-only)
- `mcp__pulumi__get-type` - Query Pulumi Registry for type schemas
- `mcp__pulumi__get-resource` - Get resource type information
- `mcp__pulumi__get-function` - Get function type information
- `mcp__pulumi__list-resources` - List available resource types
- `mcp__pulumi__list-functions` - List available function types

#### Forbidden Tools

The following tools are **FORBIDDEN** as they modify infrastructure:

- ❌ `mcp__pulumi__neo-bridge` - Launches infrastructure tasks
- ❌ `mcp__pulumi__neo-continue-task` - Continues infrastructure tasks
- ❌ `mcp__pulumi__deploy-to-aws` - Deploys infrastructure

**Attempting to use forbidden tools will raise `ValueError`.**

#### Usage Example

```python
from ra_tools.pulumi_integration import PulumiIntegration

# Initialize integration
pulumi = PulumiIntegration()

# Check availability
if pulumi.is_available():
    print(f"Pulumi MCP available - {len(pulumi.get_allowed_tools())} tools enabled")

    # Get allowed tools for ClaudeAgentOptions
    allowed_tools = pulumi.get_allowed_tools()

    # Get MCP server configuration
    mcp_config = pulumi.get_mcp_config()

    # Get infrastructure context
    context = pulumi.get_infrastructure_context()
else:
    print("Pulumi MCP unavailable - using manual documentation")
```

#### Safety Constraints

**CRITICAL**: See [CLAUDE.md:32-51](../CLAUDE.md#L32-L51) for full safety documentation.

1. **Read-only operations only** - No infrastructure modifications allowed
2. **Multi-layer enforcement**:
   - Wrapper validation (`validate_tool()` raises ValueError for forbidden tools)
   - SDK whitelist (only allowed tools in `ClaudeAgentOptions.allowed_tools`)
   - Documentation (prompts explicitly warn against forbidden tools)
3. **Graceful degradation** - Phases skip cleanly when MCP unavailable
4. **OAuth authentication** - Handled automatically by Pulumi MCP server

#### Integration Pattern

The Pulumi integration uses a **hybrid approach**:

1. **Wrapper provides**:
   - Runtime availability checking
   - Tool whitelist for `ClaudeAgentOptions.allowed_tools`
   - Safety validation (blocks forbidden tools)
   - Graceful degradation when MCP unavailable

2. **Agent accesses MCP directly**:
   - Tools called via `ClaudeAgentOptions.mcp_servers`
   - No proxy/wrapper invocation
   - Direct HTTP transport to Pulumi MCP server

**Architecture Decision**: See [ADR-003](../docs/adr/003-pulumi-mcp-integration-for-architecture-analysis.md)

#### Testing

**Unit Tests**: [tests/test_pulumi_integration.py](../tests/test_pulumi_integration.py)
- 28 tests covering all wrapper functionality
- 100% code coverage
- Tests for allowed/forbidden tool validation
- Graceful degradation scenarios

**Integration Tests**: [tests/test_architecture_orchestrator_pulumi.py](../tests/test_architecture_orchestrator_pulumi.py)
- 14 tests for orchestrator integration
- Tests with/without MCP availability
- Safety constraint validation
- Output path verification

**Run tests**:
```bash
# Unit tests only
pytest tests/test_pulumi_integration.py -v

# Integration tests only
pytest tests/test_architecture_orchestrator_pulumi.py -v

# All Pulumi-related tests
pytest tests/test_*pulumi*.py -v
```

#### Setup Instructions

See [ra_tools/pulumi_integration.py](pulumi_integration.py:211-287) for detailed setup guide.

**Quick setup**:
1. Authenticate with Pulumi Cloud at https://mcp.ai.pulumi.com/mcp
2. Verify MCP connection: `mcp list-servers | grep pulumi`
3. Test read-only access: `mcp call pulumi get-stacks`

**Troubleshooting**: If Pulumi MCP unavailable, Phase 6 will skip gracefully with helpful messages.

---

### 2. Figma MCP Integration ⚠️

**Purpose**: Design-to-code integration for Figma files.

**Status**: Experimental (MCP connected, not yet used)

**Module**: [figma_integration.py](figma_integration.py)

**Note**: This integration exists but has **not been validated** with actual agent usage. See ADR-003 for lessons learned about MCP connectivity vs working integration.

**Anti-pattern**: Do not use this as a reference - it was implemented without validation using documentation MCPs (qdrant-docs, Context7). See Pulumi integration for the correct validation pattern.

---

### 3. MCP Registry

**Purpose**: Central registry for discovering and managing MCP server connections.

**Module**: [mcp_registry.py](mcp_registry.py)

**Features**:
- Auto-discovery of available MCP servers
- Configuration requirements lookup
- Fallback options when tools unavailable
- Safety level metadata (e.g., `READ_ONLY` for Pulumi)

**Usage Example**:

```python
from ra_tools.mcp_registry import MCPRegistry

registry = MCPRegistry()

# Check server availability
if registry.is_server_available('pulumi'):
    tools = registry.get_server_tools('pulumi')
    print(f"Pulumi provides {len(tools)} tools")

# Get configuration requirements
config = registry.get_configuration_requirements('pulumi')
if config:
    print(config['setup_instructions'])
```

---

## Architecture Notes

### Why Wrappers Don't Invoke MCP Tools

The wrapper classes (e.g., `PulumiIntegration`) do **NOT** invoke MCP tools directly. Instead:

1. **Wrapper provides metadata**:
   - Runtime availability checking (`is_available()`)
   - Tool whitelist for `ClaudeAgentOptions.allowed_tools`
   - Safety validation (raises errors for forbidden tools)
   - Configuration helpers (`get_mcp_config()`)

2. **Agent invokes tools directly**:
   - Tools accessed via `ClaudeAgentOptions.mcp_servers`
   - No proxy or wrapper invocation layer
   - Direct transport to MCP server (HTTP, stdio, etc.)

**Rationale**: This separation keeps wrappers lightweight (pure Python, no async) while agents handle the actual MCP communication.

### Validation Pattern

**Before implementing new MCP integrations**, follow this validation workflow:

1. **Research using documentation MCPs**:
   - `mcp__qdrant-docs__search_docs` - Search official docs
   - `mcp__Context7__get-library-docs` - Get up-to-date code examples

2. **Validate patterns**:
   - Confirm `ClaudeAgentOptions` usage from SDK docs
   - Test graceful degradation (with/without MCP available)
   - Document findings in knowledge graph

3. **Document learnings**:
   - Use `mcp__graphiti-local__add_memory` to store patterns
   - Capture gotchas and lessons learned
   - Create integration tests

**See**: [ADR-003: Implementation Validation Requirements](../docs/adr/003-pulumi-mcp-integration-for-architecture-analysis.md#implementation-validation-requirements)

---

## Development Workflow

### Adding a New MCP Integration

1. **Research phase** (Phase 0):
   - Use `qdrant-docs` to search SDK documentation
   - Use `Context7` to get code examples
   - Document findings in knowledge graph

2. **Implementation phase** (Phase 1):
   - Create wrapper class in `ra_tools/<name>_integration.py`
   - Update `mcp_registry.py` with server metadata
   - Write comprehensive unit tests

3. **Integration phase** (Phase 2):
   - Update orchestrator to conditionally use tools
   - Add integration tests with/without MCP
   - Test graceful degradation

4. **Documentation phase** (Phase 3):
   - Update this README with usage examples
   - Document safety constraints
   - Capture lessons learned in knowledge graph

5. **Example outputs** (Phase 4):
   - Create example outputs demonstrating the integration
   - Validate outputs match expected structure

**Full workflow**: See [docs/adr/003-implementation-plan.md](../docs/adr/003-implementation-plan.md)

---

## Safety Guidelines

### Read-Only vs Write Operations

MCP integrations are categorized by safety level:

- **READ_ONLY** (e.g., Pulumi): Only query/search operations allowed
  - Multi-layer enforcement (wrapper, SDK, documentation)
  - Forbidden tools raise `ValueError`
  - Safe for autonomous agent use

- **WRITE** (future): Modify external systems
  - Requires additional safety constraints
  - User confirmation required
  - Audit logging recommended

### Forbidden Tool Enforcement

Forbidden tools are blocked at multiple layers:

1. **Wrapper validation**: `validate_tool()` raises `ValueError`
2. **SDK whitelist**: Only allowed tools in `ClaudeAgentOptions.allowed_tools`
3. **Documentation**: Prompts explicitly warn against forbidden tools
4. **Testing**: Integration tests verify forbidden tools are blocked

**Example**:
```python
pulumi = PulumiIntegration()

# This raises ValueError
try:
    pulumi.validate_tool('mcp__pulumi__neo-bridge')
except ValueError as e:
    print(e)  # "Tool 'mcp__pulumi__neo-bridge' is FORBIDDEN..."
```

---

## References

- [ADR-003: Pulumi MCP Integration](../docs/adr/003-pulumi-mcp-integration-for-architecture-analysis.md) - Architecture decision
- [ADR-003 Implementation Plan](../docs/adr/003-implementation-plan.md) - Phased implementation guide
- [CLAUDE.md:32-51](../CLAUDE.md#L32-L51) - Pulumi safety constraints
- [reference/pulumi-mcp-server.md](../reference/pulumi-mcp-server.md) - Pulumi MCP documentation

---

## Contributing

When adding new MCP integrations:

1. **Validate first** - Use documentation MCPs to research patterns
2. **Test thoroughly** - 100% test coverage, with/without MCP available
3. **Document safety** - Clearly mark read-only vs write operations
4. **Capture learnings** - Store findings in knowledge graph

**Anti-pattern**: Do not implement wrappers based on assumptions. Always validate with official SDK documentation first.
