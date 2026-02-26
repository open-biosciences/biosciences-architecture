# Repository Analyzer Framework - Implementation Checklist
**Date:** 2026-01-07
**Status:** Ready for Implementation
**Estimated Effort:** 13-18 hours
**Documentation:** https://platform.claude.com/docs/en/agent-sdk/python

---

## Overview

This plan upgrades the Repository Analyzer (RA) framework to follow official Claude Agent SDK best practices from January 2025.

**Key Benefits:**
- 🎯 Better context isolation per agent (prevents information overload)
- 🔒 Enhanced safety through PreToolUse/PostToolUse hooks
- 🛠️ Custom tools for Mermaid diagrams, dependency analysis, metrics
- 📊 Improved observability with tool execution logging

---

## Priority 1: Migrate to Programmatic Subagents

**Official SDK Recommendation:** "Programmatic definition using agents parameter (recommended for SDK applications)"
**Source:** https://docs.claude.com/en/docs/agent-sdk/subagents

### Tasks

- [ ] **Step 1.1:** Update `base_orchestrator.py` type hints
  - [ ] Change `get_agent_definitions()` return type from `Dict[str, AgentDefinition]` to `Dict[str, Dict[str, Any]]`
  - [ ] Remove `AgentDefinition` import (line 17)
  - [ ] Add `from typing import Dict, List, Optional, Any`
  - [ ] Update docstring with dict-based example
  - **File:** `ra_orchestrators/base_orchestrator.py` (lines 17, 203-209)

- [ ] **Step 1.2:** Migrate `architecture_orchestrator.py` to dict-based agents
  - [ ] Remove `from claude_agent_sdk import AgentDefinition` (line 13)
  - [ ] Add `from typing import Dict, Any`
  - [ ] Convert `analyzer` agent from AgentDefinition to dict (lines 64-80)
  - [ ] Convert `doc-writer` agent from AgentDefinition to dict (lines 82-98)
  - [ ] Update `get_agent_definitions()` return type
  - [ ] Update docstring with official SDK reference
  - **File:** `ra_orchestrators/architecture_orchestrator.py` (lines 13, 58-103)

- [ ] **Step 1.3:** Migrate `ux_orchestrator.py` to dict-based agents
  - [ ] Remove `from claude_agent_sdk import AgentDefinition` (line 15)
  - [ ] Convert `ux-researcher` to dict (lines 76-92)
  - [ ] Convert `ia-architect` to dict (lines 94-110)
  - [ ] Convert `ui-designer` to dict (lines 112-131)
  - [ ] Convert `prototype-developer` to dict (lines 133-152)
  - [ ] Update `get_agent_definitions()` return type
  - **File:** `ra_orchestrators/ux_orchestrator.py` (lines 15, 70-159)

- [ ] **Validation:** Test that agents still work with dict-based definitions
  - [ ] Run architecture orchestrator on test repo
  - [ ] Verify no `AgentDefinition` imports remain
  - [ ] Confirm `ClaudeAgentOptions(agents=...)` receives dicts

---

## Priority 2: Implement Permission Controls

**Official SDK Documentation:** "The Claude Agent SDK provides four complementary ways to control tool usage: 1. Permission Modes, 2. canUseTool callback, 3. Hooks, 4. settings.json rules"
**Source:** https://docs.claude.com/en/docs/agent-sdk/permissions

### Tasks

- [ ] **Step 2.1:** Create `permissions.py` module
  - [ ] Create new file with module docstring and imports
  - [ ] Implement `framework_protection_callback()` - canUseTool callback
    - [ ] Block writes to `ra_orchestrators/`
    - [ ] Block writes to `ra_agents/`
    - [ ] Block writes to `ra_tools/`
    - [ ] Block writes to `.venv/`
  - [ ] Implement `bash_safety_hook()` - PreToolUse hook
    - [ ] Block `rm -rf` patterns
    - [ ] Block `sudo rm` patterns
    - [ ] Block `> /dev/` patterns
    - [ ] Block `dd if=` patterns
  - [ ] Implement `file_write_validation_hook()` - PreToolUse hook
    - [ ] Block absolute paths outside project
    - [ ] Block writes to system directories
  - [ ] Implement `tool_execution_logger()` - PostToolUse hook
    - [ ] Log all tool executions
    - [ ] Detect errors in tool responses
    - [ ] Provide recovery hints
  - [ ] Implement `get_standard_hooks()` helper
    - [ ] Register PreToolUse hooks
    - [ ] Register PostToolUse hooks
  - **File:** `ra_orchestrators/permissions.py` (NEW - ~200 lines)

- [ ] **Step 2.2:** Integrate permissions into `base_orchestrator.py`
  - [ ] Add import: `from .permissions import framework_protection_callback, get_standard_hooks`
  - [ ] Update `create_client_options()` method
    - [ ] Add `can_use_tool=framework_protection_callback` parameter
    - [ ] Add `hooks=get_standard_hooks()` parameter
  - [ ] Update docstring to reference official SDK features
  - **File:** `ra_orchestrators/base_orchestrator.py` (lines 1, 255-277)

- [ ] **Validation:** Test permission controls
  - [ ] Verify framework directory writes are blocked
  - [ ] Verify dangerous bash commands are blocked
  - [ ] Verify tool execution logging works
  - [ ] Verify error detection provides hints

---

## Priority 3: Create Custom Tools

**Official SDK Documentation:** "Custom tools allow you to extend Claude Code's capabilities with your own functionality through in-process MCP servers"
**Source:** https://docs.claude.com/en/docs/agent-sdk/custom-tools

### Tasks

- [ ] **Step 3.1:** Create `custom_tools.py` module
  - [ ] Create new file with module docstring and imports
  - [ ] Implement `generate_mermaid_diagram()` tool
    - [ ] Add `@tool` decorator
    - [ ] Support `flowchart` diagram type
    - [ ] Support `sequence` diagram type
    - [ ] Return Mermaid code in markdown block
  - [ ] Implement `analyze_dependencies()` tool
    - [ ] Add `@tool` decorator
    - [ ] Support `pyproject.toml` parsing
    - [ ] Support `package.json` parsing
    - [ ] Return formatted dependency analysis
  - [ ] Implement `calculate_complexity()` tool
    - [ ] Add `@tool` decorator
    - [ ] Count decision points in Python files
    - [ ] Return complexity metrics and rating
  - **File:** `ra_tools/custom_tools.py` (NEW - ~250 lines)

- [ ] **Step 3.2:** Create `custom_mcp_server.py`
  - [ ] Create new file with imports
  - [ ] Import custom tools
  - [ ] Implement `create_ra_tools_server()` function
    - [ ] Use `create_sdk_mcp_server()` from SDK
    - [ ] Set name to "ra_tools"
    - [ ] Set version to "1.0.0"
    - [ ] Register all 3 custom tools
  - **File:** `ra_tools/custom_mcp_server.py` (NEW - ~30 lines)

- [ ] **Step 3.3:** Integrate custom tools into `base_orchestrator.py`
  - [ ] Add import: `from ra_tools.custom_mcp_server import create_ra_tools_server`
  - [ ] Update `create_client_options()` method
    - [ ] Create `ra_tools_server = create_ra_tools_server()`
    - [ ] Add `mcp_servers={"ra_tools": ra_tools_server}` parameter
  - **File:** `ra_orchestrators/base_orchestrator.py` (lines 1, 255-277)

- [ ] **Step 3.4:** Update `architecture_orchestrator.py` to expose custom tools
  - [ ] Update `get_allowed_tools()` method
    - [ ] Add `mcp__ra_tools__generate_mermaid_diagram` to tools list
    - [ ] Add `mcp__ra_tools__analyze_dependencies` to tools list
    - [ ] Add `mcp__ra_tools__calculate_complexity` to tools list
  - **File:** `ra_orchestrators/architecture_orchestrator.py` (lines 105-125)

- [ ] **Step 3.5:** Update `ux_orchestrator.py` to expose custom tools (optional)
  - [ ] Update `get_allowed_tools()` method if needed
  - **File:** `ra_orchestrators/ux_orchestrator.py` (lines 161-167)

- [ ] **Validation:** Test custom tools
  - [ ] Verify Mermaid diagram generation works
  - [ ] Verify dependency analysis extracts from pyproject.toml
  - [ ] Verify complexity calculation works
  - [ ] Verify tools appear in allowed_tools list

---

## Priority 4: Enhanced Error Handling

**Note:** Using conservative Python exception patterns (specific SDK exceptions not confirmed in official docs)

### Tasks

- [ ] **Step 4.1:** Enhance `run_with_client()` error handling
  - [ ] Add `except KeyboardInterrupt` handler
    - [ ] Print interruption message
    - [ ] Show partial results location
    - [ ] Return False
  - [ ] Add `except asyncio.TimeoutError` handler
    - [ ] Print timeout message
    - [ ] Show partial results location
    - [ ] Provide helpful tip
  - [ ] Add `except ConnectionError` handler
    - [ ] Print connection error
    - [ ] Provide troubleshooting tip
  - [ ] Enhance generic `except Exception` handler
    - [ ] Show completed phases count
    - [ ] Add traceback logging
  - **File:** `ra_orchestrators/base_orchestrator.py` (lines 290-309)

- [ ] **Step 4.2:** Add retry logic to `execute_phase()`
  - [ ] Add `max_retries: int = 2` parameter
  - [ ] Implement retry loop with error tracking
  - [ ] Add retry delay (5 seconds)
  - [ ] Print retry status messages
  - [ ] Preserve last error for final raise
  - **File:** `ra_orchestrators/base_orchestrator.py` (lines 229-253)

- [ ] **Validation:** Test error handling
  - [ ] Test Ctrl+C interruption (KeyboardInterrupt)
  - [ ] Verify partial results preserved on error
  - [ ] Verify retry logic works (simulate transient failure)
  - [ ] Verify error details logged

---

## Priority 5: Implement MCP Discovery (Optional Enhancement)

### Tasks

- [ ] **Step 5.1:** Enhance `mcp_registry.py` discovery
  - [ ] Update `discover_mcp_servers()` method
    - [ ] Check `.mcp.json` in project root
    - [ ] Check `~/.config/claude/.mcp.json`
    - [ ] Parse MCP config files
    - [ ] Call `_test_server_availability()` for each
  - [ ] Implement `_test_server_availability()` method
    - [ ] Return conservative False by default
    - [ ] Add TODO for actual health check
  - **File:** `ra_tools/mcp_registry.py` (lines 16-76)

- [ ] **Validation:** Test MCP discovery
  - [ ] Verify .mcp.json files are read
  - [ ] Verify discovered servers appear in registry
  - [ ] Verify availability checking works

---

## Testing Checklist

After implementing all priorities:

- [ ] **Smoke Test:** Run architecture orchestrator on small test repo
- [ ] **Permission Test:** Verify hooks block dangerous commands
  - [ ] Test write to `ra_orchestrators/` (should block)
  - [ ] Test `rm -rf` command (should block)
  - [ ] Test write to output dir (should allow)
- [ ] **Tool Test:** Confirm custom tools execute correctly
  - [ ] Generate a flowchart diagram
  - [ ] Analyze dependencies from pyproject.toml
  - [ ] Calculate complexity for a Python file
- [ ] **Error Test:** Trigger failure scenarios
  - [ ] Interrupt with Ctrl+C
  - [ ] Verify retry logic (disconnect network briefly)
  - [ ] Check partial results preserved
- [ ] **Integration Test:** Run full architecture analysis
  - [ ] Verify all 5 phases complete
  - [ ] Check output quality
  - [ ] Verify cost tracking works
  - [ ] Confirm tool audit logs present

---

## Documentation Updates

After successful implementation:

- [ ] Update `ra_orchestrators/CLAUDE.md`
  - [ ] Document new permission system
  - [ ] Add custom tools reference
  - [ ] Update agent definition pattern
  - [ ] Add error handling section

- [ ] Update `ra_orchestrators/README.md`
  - [ ] Add permission configuration examples
  - [ ] Document custom tools usage
  - [ ] Update error handling section

- [ ] Update `ra_tools/README.md`
  - [ ] Document custom tools API
  - [ ] Add MCP discovery configuration

- [ ] Create `ra_orchestrators/CHANGELOG.md`
  - [ ] Document breaking changes (AgentDefinition → dict)
  - [ ] List new features (permissions, custom tools)
  - [ ] Note improvements (error handling)

---

## Files Modified Summary

### Core Files (3 files)
- [x] Identified: `ra_orchestrators/base_orchestrator.py` (343 lines)
- [x] Identified: `ra_orchestrators/architecture_orchestrator.py` (410 lines)
- [x] Identified: `ra_orchestrators/ux_orchestrator.py` (623 lines)

### New Files (3 files)
- [ ] Created: `ra_orchestrators/permissions.py` (~200 lines)
- [ ] Created: `ra_tools/custom_tools.py` (~250 lines)
- [ ] Created: `ra_tools/custom_mcp_server.py` (~30 lines)

### Enhancement Files (1 file)
- [x] Identified: `ra_tools/mcp_registry.py` (185 lines)

### Documentation Files (4 files)
- [ ] Updated: `ra_orchestrators/CLAUDE.md`
- [ ] Updated: `ra_orchestrators/README.md`
- [ ] Updated: `ra_tools/README.md`
- [ ] Created: `ra_orchestrators/CHANGELOG.md`

---

## Success Metrics

Track these metrics before and after implementation:

| Metric | Before | After | Status |
|--------|--------|-------|--------|
| Context Management | Shared | Isolated per agent | ⏳ Pending |
| Permission Controls | Basic whitelist | Hooks + callbacks | ⏳ Pending |
| Custom Tools | 0 | 3+ domain-specific | ⏳ Pending |
| Error Recovery | None | Retry + graceful degradation | ⏳ Pending |
| MCP Discovery | Hardcoded | Dynamic | ⏳ Pending |

---

## Implementation Order

### Phase 1: Core SDK Alignment (4-6 hours)
1. Priority 1: Programmatic subagents
2. Priority 2: Permission controls

### Phase 2: Custom Tools (4-5 hours)
3. Priority 3: Custom tools creation and integration

### Phase 3: Robustness (4-6 hours)
4. Priority 4: Enhanced error handling
5. Priority 5: MCP discovery (optional)
6. Testing and validation
7. Documentation updates

---

## Official SDK References

All recommendations grounded in:

1. **Subagents:** https://docs.claude.com/en/docs/agent-sdk/subagents
2. **Permissions:** https://docs.claude.com/en/docs/agent-sdk/permissions
3. **Custom Tools:** https://docs.claude.com/en/docs/agent-sdk/custom-tools
4. **Python Reference:** https://docs.claude.com/en/docs/agent-sdk/python
5. **Cost Tracking:** https://docs.claude.com/en/docs/agent-sdk/cost-tracking

---

## Notes

- All changes are backward-compatible except the AgentDefinition → dict migration
- Pin `claude-agent-sdk` version before implementation for safety
- Create git commits per priority for easy rollback
- Test incrementally after each priority

---

**End of Implementation Checklist**
