"""Remove 1-liner Tool() definitions from core/tool_definitions.py."""
import re

path = "core/tool_definitions.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

targets = [
    "configure_security", "security_status",
    "get_audit_log", "get_audit_replay",
    "start_recording", "stop_recording",
    "vibe_coding_mode", "get_vibe_context",
]

for tool in targets:
    # Multi-line: Tool(name="tool", description="...",
    #     inputSchema={...}),
    pattern = rf'^\s*Tool\(name="{tool}",.*?\n\s*inputSchema=.*?\),?\s*\n?'
    text = re.sub(pattern, "", text, flags=re.MULTILINE)
    # Single-line fallback
    pattern2 = rf'^\s*Tool\(name="{tool}",.*?\),?\s*$\n?'
    text = re.sub(pattern2, "", text, flags=re.MULTILINE)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

with open(path, "r", encoding="utf-8") as f:
    remaining = [t for t in targets if t in f.read()]

print(f"Removed: {8 - len(remaining)}/8, Remaining: {remaining}")
