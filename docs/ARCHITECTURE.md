# NixOS AI Assistant - Architecture Documentation

## Overview

The NixOS AI Assistant is a system-wide smart assistant that provides natural language interface for managing NixOS systems. It's designed with a modular architecture that separates concerns and provides safety mechanisms.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                     │
├─────────────────────────────────────────────────────────────┤
│  CLI (nixos-ai)  │  Systemd Service  │  Web Interface (TBD) │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                    AI Agent Layer                          │
├─────────────────────────────────────────────────────────────┤
│  agent.py (Main AI)  │  config.py (Config)  │  watcher.py  │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                  Execution Layer                           │
├─────────────────────────────────────────────────────────────┤
│  editor.py (Files)  │  executor.py (Commands)  │  Safety    │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                  System Integration                        │
├─────────────────────────────────────────────────────────────┤
│  NixOS Module  │  Systemd Service  │  Git Integration      │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. AI Agent (`ai/agent.py`)

**Purpose**: Main coordination and natural language processing

**Responsibilities**:
- Parse user requests in natural language
- Coordinate between editor and executor
- Manage AI provider switching and fallbacks
- Handle conversation context and state
- Provide response formatting and error handling

**Key Methods**:
- `process_request()`: Main entry point for user requests
- `_execute_action()`: Route actions to appropriate components
- `_setup_ai_client()`: Initialize AI provider clients

### 2. File Editor (`ai/editor.py`)

**Purpose**: Safe file editing with validation and git integration

**Responsibilities**:
- Edit configuration files safely
- Validate NixOS syntax before applying changes
- Create git snapshots and backups
- Enforce path restrictions and permissions
- Handle file operations atomically

**Key Methods**:
- `apply_changes()`: Apply changes to files with safety checks
- `_validate_nix_file()`: Validate NixOS configuration syntax
- `_create_backup()`: Create backups before modifications
- `_commit_changes()`: Commit changes to git

### 3. Command Executor (`ai/executor.py`)

**Purpose**: Safe command execution with validation and logging

**Responsibilities**:
- Execute system commands safely
- Filter dangerous commands
- Validate commands before execution
- Log all command execution
- Handle timeouts and errors

**Key Methods**:
- `run_command()`: Execute single commands safely
- `_is_dangerous_command()`: Check for dangerous operations
- `_validate_command()`: Validate commands before execution
- `run_commands_sequence()`: Execute command sequences

### 4. Log Watcher (`ai/watcher.py`)

**Purpose**: Real-time system monitoring and feedback

**Responsibilities**:
- Monitor system logs and events
- Track service status changes
- Watch file modifications
- Provide health monitoring
- Feed information back to AI agent

**Key Methods**:
- `start()`: Start monitoring services
- `_watch_system_logs()`: Monitor system logs
- `_watch_service_status()`: Track service changes
- `get_system_health()`: Provide system health status

### 5. Configuration Manager (`ai/config.py`)

**Purpose**: Centralized configuration and AI provider management

**Responsibilities**:
- Manage multiple AI providers and API keys
- Handle configuration loading and saving
- Provide provider switching and fallbacks
- Manage security settings and permissions

**Key Methods**:
- `get_api_key()`: Retrieve API keys for providers
- `set_active_provider()`: Switch active AI provider
- `add_api_key()`: Add new API keys
- `get_model_config()`: Get model-specific settings

## Data Flow

### 1. User Request Processing

```
User Input → agent.py → AI Provider → Response Parsing → Action Routing
```

### 2. File Editing Flow

```
File Edit Request → editor.py → Path Validation → Backup Creation → 
Change Application → Syntax Validation → Git Commit → Success/Error
```

### 3. Command Execution Flow

```
Command Request → executor.py → Safety Check → Validation → 
Execution → Logging → Result Return
```

### 4. Monitoring Flow

```
System Events → watcher.py → Event Processing → AI Feedback → 
Response Generation
```

## Safety Mechanisms

### 1. Path Restrictions
- Configurable allowed paths
- System-wide access control
- Forbidden path blocking

### 2. Command Filtering
- Dangerous command detection
- Validation requirements
- Timeout protection

### 3. Git Integration
- Automatic snapshots
- Change tracking
- Easy rollback

### 4. Validation Pipeline
- NixOS syntax checking
- Configuration testing
- Pre-application validation

## AI Provider Integration

### Supported Providers
- **OpenAI**: GPT-4, GPT-3.5-turbo
- **Anthropic**: Claude-3-opus, Claude-3-sonnet
- **Ollama**: Local models (llama2, codellama)

### Provider Management
- Multiple API key support
- Automatic fallback switching
- Model-specific configuration
- Rate limiting and timeouts

## Security Model

### 1. Permission Levels
- **Read-only**: System information access
- **Limited Write**: AI directory only
- **System-wide**: Full system access (dangerous)

### 2. Command Restrictions
- **Allowed**: Safe system commands
- **Restricted**: Commands requiring confirmation
- **Forbidden**: Dangerous operations

### 3. Network Security
- Configurable domain allowlists
- Port restrictions
- API key protection

## State Management

### 1. Persistent State
- Configuration files
- Git repository
- Log files
- Cache directory

### 2. Runtime State
- AI conversation context
- Active provider settings
- Monitoring status
- Command history

## Error Handling

### 1. Graceful Degradation
- Fallback AI providers
- Mock responses when APIs unavailable
- Safe error messages

### 2. Recovery Mechanisms
- Automatic rollback on failures
- Git-based recovery
- Service restart capabilities

### 3. Logging and Monitoring
- Comprehensive logging
- Error tracking
- Performance monitoring

## Extension Points

### 1. New AI Providers
- Implement provider interface
- Add to configuration
- Update client initialization

### 2. New Command Types
- Extend executor validation
- Add safety checks
- Update permission system

### 3. New File Types
- Add file type detection
- Implement type-specific validation
- Update editor capabilities

## Performance Considerations

### 1. Async Operations
- Non-blocking I/O
- Concurrent command execution
- Parallel monitoring

### 2. Caching
- Model response caching
- Configuration caching
- File change detection

### 3. Resource Management
- Memory limits
- CPU quotas
- Network restrictions

## Future Enhancements

### 1. Web Interface
- REST API
- WebSocket connections
- Real-time updates

### 2. Plugin System
- Custom command handlers
- Provider plugins
- Extension framework

### 3. Multi-user Support
- User isolation
- Permission management
- Audit logging

## Development Guidelines

### 1. Code Organization
- Single responsibility principle
- Clear interfaces
- Comprehensive testing

### 2. Safety First
- Validate all inputs
- Test all changes
- Maintain rollback capability

### 3. Documentation
- Keep architecture updated
- Document all APIs
- Provide examples
