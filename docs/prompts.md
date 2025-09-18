# Prompt Engineering Guide

This guide explains how to customize the AI agent's prompts and behavior for better results.

## Overview

The AI agent uses a structured prompt system to generate unified-diff patches for NixOS configuration changes. The prompts are stored in `ai-agent/prompts.json` and can be customized to improve accuracy and add new capabilities.

## Prompt Structure

### System Prompt

The system prompt defines the AI's role and constraints:

```json
{
  "system_prompt": "You are a NixOS configuration patch generator. Your job is to generate unified diff patches that modify NixOS configuration files.\n\nRULES:\n1. Output ONLY a unified diff patch in git format\n2. If you cannot generate a safe patch, return exactly: UNABLE_TO_GENERATE_PATCH\n3. Preserve existing formatting and style\n4. Make minimal, targeted changes\n5. Use proper Nix syntax\n6. Include proper file paths in the diff header"
}
```

### Examples

The examples section provides few-shot learning examples:

```json
{
  "examples": [
    {
      "input": "TARGET: /etc/nixos/configuration.nix\nINSTRUCTION: Add pkgs.vscode to environment.systemPackages",
      "output": "diff --git a/configuration.nix b/configuration.nix\nindex 1234567..abcdef0 100644\n--- a/configuration.nix\n+++ b/configuration.nix\n@@ -15,7 +15,8 @@\n   environment.systemPackages = with pkgs; [\n     firefox\n     git\n+    vscode\n   ];"
    }
  ]
}
```

## Customizing Prompts

### Adding New Examples

To add new examples, edit `ai-agent/prompts.json`:

```json
{
  "examples": [
    {
      "input": "TARGET: profiles/desktop.nix\nINSTRUCTION: Add a new wallpaper to the wallpaper picker",
      "output": "diff --git a/profiles/desktop.nix b/profiles/desktop.nix\nindex 1234567..abcdef0 100644\n--- a/profiles/desktop.nix\n+++ b/profiles/desktop.nix\n@@ -25,6 +25,8 @@\n   # Wallpaper configuration\n   services.xserver.windowManager.hyprland.extraConfig = ''\n     exec-once = swww init\n+    exec-once = swww img ~/Pictures/wallpapers/new-wallpaper.jpg\n+    bind = SUPER, W, exec, swww img ~/Pictures/wallpapers/$(ls ~/Pictures/wallpapers/ | shuf -n1)\n   '';\n }"
    }
  ]
}
```

### Modifying System Rules

Update the system prompt to add new rules or constraints:

```json
{
  "system_prompt": "You are a NixOS configuration patch generator. Your job is to generate unified diff patches that modify NixOS configuration files.\n\nRULES:\n1. Output ONLY a unified diff patch in git format\n2. If you cannot generate a safe patch, return exactly: UNABLE_TO_GENERATE_PATCH\n3. Preserve existing formatting and style\n4. Make minimal, targeted changes\n5. Use proper Nix syntax\n6. Include proper file paths in the diff header\n7. Always add comments explaining complex changes\n8. Use consistent indentation (2 spaces)"
}
```

### Adding Fallback Prompts

Define prompts for fallback scenarios:

```json
{
  "fallback_prompts": {
    "flatpak_install": "Generate a patch to install {package} via flatpak",
    "appimage_wrapper": "Generate a wrapper script and desktop file for {package} AppImage",
    "docker_wrapper": "Generate a Docker wrapper for {package} with GUI support"
  }
}
```

## Prompt Templates

### Package Installation

```json
{
  "input": "TARGET: /etc/nixos/configuration.nix\nINSTRUCTION: Add {package} to environment.systemPackages",
  "output": "diff --git a/configuration.nix b/configuration.nix\nindex 1234567..abcdef0 100644\n--- a/configuration.nix\n+++ b/configuration.nix\n@@ -15,7 +15,8 @@\n   environment.systemPackages = with pkgs; [\n     firefox\n     git\n+    {package}\n   ];"
}
```

### Service Configuration

```json
{
  "input": "TARGET: /etc/nixos/configuration.nix\nINSTRUCTION: Enable {service} service",
  "output": "diff --git a/configuration.nix b/configuration.nix\nindex 1234567..abcdef0 100644\n--- a/configuration.nix\n+++ b/configuration.nix\n@@ -20,6 +20,8 @@\n   services.xserver.enable = true;\n \n+  services.{service}.enable = true;\n+\n   # ... rest of config\n }"
}
```

### User Configuration

```json
{
  "input": "TARGET: /etc/nixos/configuration.nix\nINSTRUCTION: Add user {username} with {groups} groups",
  "output": "diff --git a/configuration.nix b/configuration.nix\nindex 1234567..abcdef0 100644\n--- a/configuration.nix\n+++ b/configuration.nix\n@@ -10,6 +10,12 @@\n   users.users.nixos = {\n     isNormalUser = true;\n     extraGroups = [ \"wheel\" ];\n   };\n \n+  users.users.{username} = {\n+    isNormalUser = true;\n+    extraGroups = {groups};\n+  };\n+\n   # ... rest of config\n }"
}
```

## Best Practices

### 1. Keep Examples Relevant

Only include examples that are commonly used and represent good patterns:

```json
{
  "examples": [
    {
      "input": "TARGET: /etc/nixos/configuration.nix\nINSTRUCTION: Add pkgs.firefox to environment.systemPackages",
      "output": "// Good: Simple, clear example"
    },
    {
      "input": "TARGET: /etc/nixos/configuration.nix\nINSTRUCTION: Add 50 different packages with complex configuration",
      "output": "// Bad: Too complex, not representative"
    }
  ]
}
```

### 2. Use Consistent Formatting

Ensure all examples follow the same format:

```json
{
  "input": "TARGET: {file_path}\nINSTRUCTION: {instruction}",
  "output": "diff --git a/{file_path} b/{file_path}\nindex 1234567..abcdef0 100644\n--- a/{file_path}\n+++ b/{file_path}\n@@ -{line_number},{line_count} +{line_number},{line_count} @@\n   {context}\n+  {addition}\n   {context}"
}
```

### 3. Include Error Handling

Add examples for common error scenarios:

```json
{
  "examples": [
    {
      "input": "TARGET: /etc/nixos/configuration.nix\nINSTRUCTION: Add invalid package name",
      "output": "UNABLE_TO_GENERATE_PATCH"
    }
  ]
}
```

### 4. Test Your Prompts

Always test new prompts before deploying:

```bash
# Test with a simple example
python -c "
from ai_agent.llm_adapter import LLMAdapter
adapter = LLMAdapter({'llm_provider': 'openai', 'api_key': 'your-key'})
result = await adapter.generate_patch(['/etc/nixos/configuration.nix'], 'Add pkgs.hello')
print(result)
"
```

## Advanced Techniques

### 1. Context-Aware Prompts

Include context information in prompts:

```python
def _create_prompt(self, target_files, instruction, context):
    prompt = self.prompts['system_prompt']
    
    # Add context information
    if context.get('packages'):
        prompt += f"\nCONTEXT: Working with packages: {', '.join(context['packages'])}"
    
    if context.get('components'):
        prompt += f"\nCONTEXT: System components: {', '.join(context['components'])}"
    
    # Add current request
    prompt += f"\n\nINPUT:\nTARGET: {', '.join(target_files)}\nINSTRUCTION: {instruction}"
    
    return prompt
```

### 2. Dynamic Prompt Selection

Select different prompts based on the request type:

```python
def get_prompt_for_intent(self, intent):
    if intent['type'] == 'package_installation':
        return self.prompts['package_installation_prompt']
    elif intent['type'] == 'service_configuration':
        return self.prompts['service_configuration_prompt']
    else:
        return self.prompts['system_prompt']
```

### 3. Prompt Validation

Validate prompts before using them:

```python
def validate_prompt(self, prompt):
    required_elements = ['system_prompt', 'examples']
    
    for element in required_elements:
        if element not in prompt:
            raise ValueError(f"Missing required element: {element}")
    
    if not isinstance(prompt['examples'], list):
        raise ValueError("Examples must be a list")
    
    return True
```

## Troubleshooting

### Common Issues

**AI generates invalid patches:**
- Add more examples for the specific use case
- Check if the system prompt is clear about constraints
- Verify that the input format is consistent

**AI returns UNABLE_TO_GENERATE_PATCH too often:**
- Add more examples for complex scenarios
- Simplify the system prompt
- Check if the instruction is clear and specific

**AI makes incorrect changes:**
- Add negative examples showing what not to do
- Include more context in the prompt
- Use more specific instructions

### Debugging Prompts

Enable debug logging to see the actual prompts being sent:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# The LLM adapter will now log the full prompts
```

## Examples Repository

For more examples and templates, check the `examples/` directory in the repository.

---

**Happy prompt engineering! 🚀**
