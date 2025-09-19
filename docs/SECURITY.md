# NixOS AI Assistant - Security Documentation

## Security Overview

The NixOS AI Assistant is designed with security as a primary concern. This document outlines the security model, potential risks, and mitigation strategies.

## Threat Model

### 1. External Threats
- **Malicious API responses**: AI providers returning harmful commands
- **Network attacks**: Man-in-the-middle, API key theft
- **Supply chain attacks**: Compromised dependencies

### 2. Internal Threats
- **Privilege escalation**: AI gaining unauthorized system access
- **Data exfiltration**: Sensitive information leakage
- **System modification**: Unauthorized configuration changes

### 3. User Errors
- **Misconfiguration**: Incorrect security settings
- **Dangerous commands**: User requesting harmful operations
- **API key exposure**: Credentials in logs or configs

## Security Architecture

### 1. Defense in Depth

```
┌─────────────────────────────────────────────────────────────┐
│                    User Input Validation                    │
├─────────────────────────────────────────────────────────────┤
│  Command Filtering  │  Path Restrictions  │  Permission     │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                    Execution Sandbox                       │
├─────────────────────────────────────────────────────────────┤
│  Process Isolation  │  Resource Limits  │  Network Control │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                    System Integration                      │
├─────────────────────────────────────────────────────────────┤
│  Git Snapshots  │  Rollback System  │  Audit Logging      │
└─────────────────────────────────────────────────────────────┘
```

### 2. Security Layers

#### Layer 1: Input Validation
- Natural language parsing validation
- Command syntax checking
- Path existence verification
- Parameter sanitization

#### Layer 2: Permission System
- File access restrictions
- Command execution limits
- Network access control
- User privilege management

#### Layer 3: Execution Sandbox
- Process isolation
- Resource limits
- Network restrictions
- File system boundaries

#### Layer 4: Monitoring and Recovery
- Comprehensive logging
- Real-time monitoring
- Automatic rollback
- Incident response

## Security Features

### 1. Access Control

#### File System Permissions
```json
{
  "file_permissions": {
    "read": ["/etc/nixos/nixos-ai/**/*"],
    "write": ["/etc/nixos/nixos-ai/**/*"],
    "forbidden": ["/etc/passwd", "/etc/shadow", "/root/**/*"]
  }
}
```

#### Command Restrictions
```json
{
  "command_permissions": {
    "allowed": ["nixos-rebuild", "systemctl", "git"],
    "restricted": ["rm -rf", "dd if=", "mkfs"],
    "forbidden": ["rm -rf /", "shutdown -h now"]
  }
}
```

### 2. API Key Management

#### Secure Storage
- Environment variables for sensitive data
- Keyring integration for persistent storage
- No hardcoded credentials
- API key rotation support

#### Access Control
- Provider-specific API keys
- Rate limiting and quotas
- Network restrictions
- Audit logging

### 3. Network Security

#### Outbound Connections
- Whitelist allowed domains
- Port restrictions
- TLS/SSL enforcement
- Certificate validation

#### Inbound Connections
- Local-only by default
- Optional network access
- Authentication required
- Rate limiting

### 4. Process Security

#### Isolation
- Dedicated user account
- Process sandboxing
- Resource limits
- No privilege escalation

#### Monitoring
- Process activity logging
- Resource usage tracking
- Anomaly detection
- Alert system

## Configuration Security

### 1. Secure Defaults

#### Minimal Permissions
```nix
services.nixos-ai = {
  enable = true;
  enableSystemWideAccess = false;  # Default: false
  allowedPaths = [ "/etc/nixos/nixos-ai" ];
  restrictNetwork = true;  # Default: true
};
```

#### Safe Commands Only
```json
{
  "safety_settings": {
    "require_confirmation_for_dangerous_commands": true,
    "auto_rollback_on_failure": true,
    "log_all_actions": true
  }
}
```

### 2. Environment Variables

#### Required Variables
```bash
NIXOS_AI_DIR="/etc/nixos/nixos-ai"
AI_ACTIVE_PROVIDER="openai"
ALLOWED_PATHS="/etc/nixos/nixos-ai"
SYSTEM_WIDE_ACCESS="false"
```

#### API Key Variables
```bash
OPENAI_API_KEY="sk-..."
ANTHROPIC_API_KEY="sk-ant-..."
OLLAMA_API_KEY=""  # Optional for local
```

### 3. File Permissions

#### Directory Structure
```
/etc/nixos/nixos-ai/
├── ai/                    # 755 root:root
├── logs/                  # 755 root:root
├── state/                 # 755 root:root
├── cache/                 # 755 root:root
├── backups/               # 755 root:root
└── config.json            # 600 root:root
```

## Risk Assessment

### 1. High Risk Scenarios

#### System-wide Access Enabled
- **Risk**: AI can modify any system file
- **Mitigation**: Require explicit confirmation, comprehensive logging
- **Recommendation**: Keep disabled unless absolutely necessary

#### Dangerous Commands
- **Risk**: AI executes harmful system commands
- **Mitigation**: Command filtering, validation, confirmation
- **Recommendation**: Use whitelist approach

#### API Key Exposure
- **Risk**: Credentials leaked in logs or configs
- **Mitigation**: Secure storage, environment variables
- **Recommendation**: Regular key rotation

### 2. Medium Risk Scenarios

#### Network Access
- **Risk**: Unauthorized external connections
- **Mitigation**: Domain whitelisting, network restrictions
- **Recommendation**: Monitor network activity

#### File System Access
- **Risk**: Unauthorized file modifications
- **Mitigation**: Path restrictions, permission checks
- **Recommendation**: Regular access audits

### 3. Low Risk Scenarios

#### Configuration Changes
- **Risk**: Unintended system modifications
- **Mitigation**: Git snapshots, rollback capability
- **Recommendation**: Test changes in safe environment

## Incident Response

### 1. Detection

#### Monitoring
- Real-time log analysis
- Anomaly detection
- Performance monitoring
- Security alerts

#### Indicators
- Unusual command patterns
- Unexpected file modifications
- Network anomalies
- Resource usage spikes

### 2. Response

#### Immediate Actions
1. Stop AI service
2. Isolate affected systems
3. Preserve evidence
4. Notify administrators

#### Investigation
1. Analyze logs
2. Identify attack vector
3. Assess damage
4. Document findings

#### Recovery
1. Restore from backup
2. Apply security patches
3. Update configurations
4. Monitor for recurrence

### 3. Prevention

#### Regular Updates
- Keep dependencies updated
- Apply security patches
- Update AI models
- Review configurations

#### Security Audits
- Regular access reviews
- Permission audits
- Log analysis
- Penetration testing

## Best Practices

### 1. Configuration

#### Secure Setup
- Use minimal permissions
- Enable all safety features
- Regular security updates
- Monitor system activity

#### API Key Management
- Use environment variables
- Rotate keys regularly
- Monitor usage
- Implement rate limiting

### 2. Operation

#### Safe Usage
- Test changes in safe environment
- Review AI actions before applying
- Keep backups current
- Monitor system health

#### Incident Prevention
- Regular security training
- Update procedures
- Test recovery processes
- Maintain documentation

### 3. Development

#### Secure Coding
- Input validation
- Output sanitization
- Error handling
- Logging security events

#### Testing
- Security testing
- Penetration testing
- Vulnerability scanning
- Code review

## Compliance

### 1. Data Protection
- No personal data storage
- Minimal logging
- Secure data handling
- Regular purging

### 2. Audit Requirements
- Comprehensive logging
- Change tracking
- Access monitoring
- Incident documentation

### 3. Regulatory Compliance
- Follow security standards
- Implement controls
- Regular assessments
- Documentation maintenance

## Security Checklist

### Installation
- [ ] Use secure defaults
- [ ] Set up proper permissions
- [ ] Configure network restrictions
- [ ] Enable all safety features

### Configuration
- [ ] Use environment variables for secrets
- [ ] Restrict file system access
- [ ] Enable command filtering
- [ ] Set up monitoring

### Operation
- [ ] Regular security updates
- [ ] Monitor system activity
- [ ] Review AI actions
- [ ] Test recovery procedures

### Maintenance
- [ ] Regular security audits
- [ ] Update dependencies
- [ ] Rotate API keys
- [ ] Review configurations

## Contact and Support

For security issues or questions:
- Create a security issue on GitHub
- Contact maintainers directly
- Follow responsible disclosure
- Provide detailed information

## Changelog

- **v1.0.0**: Initial security documentation
- **v1.1.0**: Added API key management
- **v1.2.0**: Enhanced monitoring and logging
