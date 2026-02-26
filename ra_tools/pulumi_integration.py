"""Pulumi MCP integration wrapper (READ-ONLY operations only).

CRITICAL SAFETY CONSTRAINTS:
- Only read-only Pulumi tools allowed
- FORBIDDEN: neo-bridge, neo-continue-task, deploy-to-aws
- See CLAUDE.md:32-51 for safety documentation

This wrapper provides runtime validation and configuration helpers for Pulumi MCP integration.
The agent accesses Pulumi MCP DIRECTLY via ClaudeAgentOptions.mcp_servers.
The wrapper does NOT invoke MCP tools - it only provides availability checking and graceful degradation.
"""

import os
from typing import Any


class PulumiIntegration:
    """Wrapper for Pulumi MCP server integration (READ-ONLY).

    This class provides:
    1. Runtime availability checking for Pulumi MCP server
    2. Tool whitelist for ClaudeAgentOptions.allowed_tools
    3. Safety validation (blocks forbidden tools)
    4. Graceful degradation when MCP unavailable

    The agent accesses Pulumi MCP directly via ClaudeAgentOptions.mcp_servers.
    This wrapper does NOT invoke tools - that's done by the agent via SDK.
    """

    # Whitelisted read-only tools
    ALLOWED_TOOLS = [
        'mcp__pulumi__get-stacks',
        'mcp__pulumi__resource-search',
        'mcp__pulumi__get-policy-violations',
        'mcp__pulumi__get-users',
        'mcp__pulumi__neo-get-tasks',  # Read-only task listing
        'mcp__pulumi__get-type',
        'mcp__pulumi__get-resource',
        'mcp__pulumi__get-function',
        'mcp__pulumi__list-resources',
        'mcp__pulumi__list-functions',
    ]

    # Forbidden tools (infrastructure modification)
    FORBIDDEN_TOOLS = [
        'mcp__pulumi__neo-bridge',
        'mcp__pulumi__neo-continue-task',
        'mcp__pulumi__deploy-to-aws',
    ]

    def __init__(self):
        """Initialize Pulumi integration.

        Checks MCP server availability at runtime.
        """
        self.mcp_available = self._check_mcp_availability()
        self.organization = os.getenv('PULUMI_ORG', 'donbr')

    def _check_mcp_availability(self) -> bool:
        """Verify Pulumi MCP server is connected.

        Returns:
            True if Pulumi MCP server is accessible

        Note:
            This is a simplified check. In production, you might:
            - Call a lightweight MCP tool (like get-stacks) to verify connectivity
            - Catch connection/auth errors
            - Cache the result with TTL
        """
        # TODO: Implement actual MCP availability check
        # Strategy from Phase 0 research:
        # - Try calling a read-only tool (get-stacks)
        # - Catch connection errors
        # - Return boolean

        # Placeholder implementation - assumes MCP is available if configured
        # In production, should actually test connectivity
        return True  # Optimistic default for now

    def is_available(self) -> bool:
        """Check if Pulumi MCP integration is available.

        Returns:
            True if MCP server is connected and authenticated
        """
        return self.mcp_available

    def get_allowed_tools(self) -> list[str]:
        """Get list of whitelisted Pulumi tools.

        This list should be used in ClaudeAgentOptions.allowed_tools
        to restrict which Pulumi MCP tools the agent can access.

        Returns:
            List of tool names safe for read-only operations
        """
        return self.ALLOWED_TOOLS.copy()

    def validate_tool(self, tool_name: str) -> bool:
        """Validate that a tool is allowed.

        Args:
            tool_name: Tool name to validate (e.g., "mcp__pulumi__get-stacks")

        Returns:
            True if tool is whitelisted

        Raises:
            ValueError: If tool is in forbidden list
        """
        if tool_name in self.FORBIDDEN_TOOLS:
            raise ValueError(
                f"Tool '{tool_name}' is FORBIDDEN - it modifies infrastructure. "
                f'Only read-only operations allowed. See CLAUDE.md:32-51'
            )

        return tool_name in self.ALLOWED_TOOLS

    def get_mcp_config(self) -> dict[str, Any]:
        """Get MCP server configuration for ClaudeAgentOptions.

        Returns:
            Dictionary with MCP server configuration for Pulumi

        Example:
            >>> pulumi = PulumiIntegration()
            >>> config = pulumi.get_mcp_config()
            >>> # Use in ClaudeAgentOptions:
            >>> options = ClaudeAgentOptions(
            ...     mcp_servers={'pulumi': config}, allowed_tools=pulumi.get_allowed_tools()
            ... )
        """
        return {
            'type': 'http',
            'url': 'https://mcp.ai.pulumi.com/mcp',
            # OAuth authentication handled automatically by MCP server
        }

    def get_infrastructure_context(self, stack_name: str | None = None) -> dict[str, Any]:
        """Get infrastructure context for documentation.

        NOTE: This method provides metadata and instructions.
        The actual MCP tool calls (get-stacks, resource-search) are made
        by the AGENT, not by this wrapper.

        Args:
            stack_name: Optional stack name to filter by

        Returns:
            Dictionary with infrastructure metadata and instructions
        """
        if not self.is_available():
            return {
                'error': 'Pulumi MCP not available',
                'fallback': 'Use manual infrastructure documentation',
                'instructions': self.get_setup_instructions(),
            }

        # Return metadata and instructions for the agent
        return {
            'organization': self.organization,
            'stack_filter': stack_name,
            'recommended_tools': [
                'mcp__pulumi__get-stacks - List all Pulumi stacks',
                'mcp__pulumi__resource-search - Search cloud resources',
                'mcp__pulumi__get-policy-violations - Check compliance',
            ],
            'example_queries': {
                'list_stacks': 'Use get-stacks to list all stacks in organization',
                's3_buckets': 'resource-search query="type:aws:s3/bucket:Bucket" top=20',
                'lambda_functions': 'resource-search query="type:aws:lambda/function:Function"',
            },
            'note': 'Agent calls MCP tools directly via ClaudeAgentOptions.mcp_servers',
        }

    def search_resources(self, query: str, top: int = 20) -> dict[str, Any]:
        """Get resource search instructions for the agent.

        NOTE: This method does NOT call resource-search itself.
        It provides instructions for the AGENT to call mcp__pulumi__resource-search.

        Args:
            query: Lucene query (e.g., "type:aws:s3/bucket:Bucket")
            top: Maximum results to return

        Returns:
            Dictionary with search instructions for the agent
        """
        if not self.is_available():
            return {
                'error': 'Pulumi MCP unavailable',
                'instructions': self.get_setup_instructions(),
            }

        return {
            'tool_to_call': 'mcp__pulumi__resource-search',
            'parameters': {'query': query, 'top': top, 'org': self.organization},
            'lucene_syntax_help': {
                'examples': [
                    'type:aws:s3/bucket:Bucket - Find all S3 buckets',
                    'type:aws:lambda/function:Function - Find Lambda functions',
                    'package:aws - All AWS resources',
                    'module:s3 - All S3 resources (both aws and aws-native)',
                    '-.tags: - Resources WITHOUT tags property',
                ]
            },
            'note': 'Agent calls mcp__pulumi__resource-search directly via SDK',
        }

    def get_setup_instructions(self) -> str:
        """Get setup instructions for Pulumi MCP.

        Returns:
            Markdown-formatted setup guide
        """
        return """
# Pulumi MCP Integration Setup

## Prerequisites

1. Pulumi Cloud account (free tier available)
2. Pulumi MCP server configured in Claude Code

## Configuration Steps

### 1. Authenticate with Pulumi Cloud

The Pulumi MCP server uses OAuth authentication:

```bash
# Authentication is handled automatically by MCP server
# Visit: https://mcp.ai.pulumi.com/mcp
```

### 2. Verify MCP Connection

```bash
# Check Pulumi MCP is connected
mcp list-servers | grep pulumi

# List available tools
mcp list-tools pulumi
```

### 3. Test Read-Only Access

```bash
# Should work (read-only)
mcp call pulumi get-stacks

# Should fail (infrastructure modification)
mcp call pulumi neo-bridge  # FORBIDDEN
```

## Troubleshooting

**"Pulumi MCP not available"**:
- Verify MCP server is running: `mcp list-servers`
- Check authentication: Visit Pulumi Cloud console
- Restart Claude Code if needed

**"Tool is FORBIDDEN"**:
- Only read-only tools allowed in this environment
- See CLAUDE.md:32-51 for safety constraints
- Use Pulumi Cloud console for infrastructure changes

## Manual Fallback

If Pulumi MCP unavailable:
1. Document infrastructure manually in markdown
2. Use Pulumi Cloud console for resource inventory
3. Export stack outputs to JSON for reference

## Architecture Notes

This wrapper provides:
- Runtime availability checking
- Tool whitelist for ClaudeAgentOptions.allowed_tools
- Safety validation (blocks forbidden tools)
- Graceful degradation when MCP unavailable

The agent accesses Pulumi MCP DIRECTLY via ClaudeAgentOptions.mcp_servers.
The wrapper does NOT invoke tools - that's done by the agent via SDK.

See ADR-003 and implementation plan for full details.
"""


# Testing stub for development
if __name__ == '__main__':
    pulumi = PulumiIntegration()
    print(f'Pulumi MCP Available: {pulumi.is_available()}')
    print(f'Allowed Tools: {len(pulumi.get_allowed_tools())} tools')
    print('\nMCP Config:')
    print(f'  {pulumi.get_mcp_config()}')
    print('\nSetup Instructions:\n')
    print(pulumi.get_setup_instructions())
