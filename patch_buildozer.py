#!/usr/bin/env python3
"""
Patch buildozer to skip root check in CI environments.
This is more reliable than PowerShell regex replacements.
"""
import sys
import re

def patch_buildozer(file_path):
    """Patch buildozer __init__.py to disable root check."""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    patches_applied = []

    # Patch 1: Make check_root() return immediately (most thorough)
    if 'def check_root(self):' in content:
        # Find the method and add return statement
        pattern = r'(def check_root\(self\):)'
        replacement = r'\1\n        return  # Patched: skip root check in CI'
        content = re.sub(pattern, replacement, content)
        if content != original_content:
            patches_applied.append("check_root() early return")
            original_content = content

    # Patch 2: Disable the if hasattr(os, 'getuid') check
    pattern = r"if hasattr\(os,\s*['\"]getuid['\"]\):"
    if re.search(pattern, content):
        content = re.sub(pattern, "if False and hasattr(os, 'getuid'):", content)
        if content != original_content:
            patches_applied.append("hasattr getuid check")
            original_content = content

    # Patch 3: Disable if os.getuid() == 0
    pattern = r"if os\.getuid\(\)\s*==\s*0:"
    if re.search(pattern, content):
        content = re.sub(pattern, "if False:", content)
        if content != original_content:
            patches_applied.append("getuid() == 0 check")
            original_content = content

    # Patch 4: Replace input() call to avoid EOFError in CI
    pattern = r"cont = input\('Are you sure you want to continue"
    if re.search(pattern, content):
        content = re.sub(
            pattern,
            "cont = 'y'  # Patched: auto-continue in CI # input('Are you sure you want to continue",
            content
        )
        if content != original_content:
            patches_applied.append("input() call disabled")
            original_content = content

    # Write patched content
    if patches_applied:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[OK] Successfully patched buildozer: {', '.join(patches_applied)}")
        return True
    else:
        print("[WARN] No patches were applied (may already be patched or code structure changed)")
        return False

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python patch_buildozer.py <path_to_buildozer_init.py>")
        sys.exit(1)

    file_path = sys.argv[1]
    success = patch_buildozer(file_path)
    sys.exit(0 if success else 1)
