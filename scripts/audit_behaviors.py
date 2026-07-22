import os, re, json

behaviors_dir = 'behaviors'
dirs = sorted([d for d in os.listdir(behaviors_dir) if os.path.isdir(os.path.join(behaviors_dir, d)) and os.path.exists(os.path.join(behaviors_dir, d, d + '.gd'))])

no_tool = []
no_warnings = []
no_signal_emit = []
class_mismatch = []
no_init_resources = []

for d in dirs:
    gd_path = os.path.join(behaviors_dir, d, d + '.gd')
    bj_path = os.path.join(behaviors_dir, d, 'behavior.json')
    
    with open(gd_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # @tool
    if '@tool' not in content:
        no_tool.append(d)
    
    # class_name matches expected
    cn = re.search(r'class_name\s+(\w+)', content)
    if cn:
        expected = ''.join(w.capitalize() for w in d.split('_'))
        if cn.group(1) != expected:
            class_mismatch.append(f"{d}: {cn.group(1)} (expected {expected})")
    
    # _get_configuration_warnings
    if '_get_configuration_warnings' not in content:
        no_warnings.append(d)
    
    # signals not emitted
    signals = re.findall(r'signal\s+(\w+)', content)
    for s in signals:
        if f'{s}.emit' not in content:
            no_signal_emit.append(f'{d}:{s}')
    
    # _initialized missing when _ready creates resources
    ready_match = re.search(r'func _ready\(\)[^:]*:(.*?)(?=\nfunc |\n$)', content, re.DOTALL)
    if ready_match:
        ready_body = ready_match.group(1)
        creates = ('.new()' in ready_body or 'add_child' in ready_body or 
                   'create_tween' in ready_body or 'Timer.new' in ready_body)
        if creates and '_initialized' not in content:
            no_init_resources.append(d)

print(f"Total behaviors: {len(dirs)}")
print(f"\n--- CRITICAL ---")
print(f"no @tool: {len(no_tool)}")
for x in no_tool: print(f"  {x}")
print(f"\nno _get_configuration_warnings: {len(no_warnings)}")
for x in no_warnings: print(f"  {x}")
print(f"\nsignals not emitted: {len(no_signal_emit)}")
for x in no_signal_emit: print(f"  {x}")
print(f"\n--- WARNINGS ---")
print(f"class_name mismatch: {len(class_mismatch)}")
for x in class_mismatch: print(f"  {x}")
print(f"no _initialized (creates resources in _ready): {len(no_init_resources)}")
for x in no_init_resources: print(f"  {x}")
