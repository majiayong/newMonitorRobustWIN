#!/usr/bin/env python3
"""
Patch buildozer to work on Windows.
This patches both the root check and the Windows platform check.
"""
import sys
import re
import os

def patch_buildozer_init(file_path):
    """Patch buildozer __init__.py to disable root check."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    patches_applied = []

    # Patch 1: Make check_root() return immediately
    if 'def check_root(self):' in content:
        pattern = r'(def check_root\(self\):)'
        replacement = r'\1\n        return  # Patched: skip root check in CI'
        content = re.sub(pattern, replacement, content)
        if content != original_content:
            patches_applied.append("check_root() early return")
            original_content = content

    # Patch 2: Replace input() call to avoid EOFError
    pattern = r"cont = input\('Are you sure you want to continue"
    if re.search(pattern, content):
        content = re.sub(
            pattern,
            "cont = 'y'  # Patched: auto-continue # input('Are you sure you want to continue",
            content
        )
        if content != original_content:
            patches_applied.append("input() call disabled")
            original_content = content

    # Patch 3: Fix PATH separator in checkbin for Windows + add debug
    pattern = r"(    def checkbin\(self, msg, fn\):)\n(        self\.debug\('Search for \{0\}'\.format\(msg\)\))"
    if re.search(pattern, content):
        replacement = r"\1\n\2\n        # DEBUG: Print PATH\n        import sys\n        self.debug('PATH separator: ' + repr(os.pathsep))\n        self.debug('PATH value: ' + environ.get('PATH', 'NOT SET')[:200])"
        content = re.sub(pattern, replacement, content)
        if content != original_content:
            patches_applied.append("checkbin debug added")
            original_content = content

    # Patch 4: Replace entire checkbin method with Windows-compatible version
    pattern = r"    def checkbin\(self, msg, fn\):.*?(?=\n    def )"
    if re.search(pattern, content, re.DOTALL):
        replacement = """    def checkbin(self, msg, fn):
        # Patched: Use shutil.which with buildozer's environment
        from shutil import which
        from os import environ as os_environ
        self.debug('Search for {0}'.format(msg))

        # Merge system environment with buildozer's environment
        env = os_environ.copy()
        env.update(self.environ)

        # Search in the merged PATH
        result = which(fn, path=env.get('PATH'))
        if result:
            self.debug(' -> found at {0}'.format(result))
            return result
        self.error('{} not found, please install it.'.format(msg))
        exit(1)

"""
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        if content != original_content:
            patches_applied.append("checkbin uses buildozer environment")
            original_content = content

    if patches_applied:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return patches_applied
    return []

def patch_android_target(targets_dir):
    """Patch buildozer/targets/android.py to allow Windows."""
    android_py = os.path.join(targets_dir, 'android.py')
    if not os.path.exists(android_py):
        return []

    with open(android_py, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    patches_applied = []

    # Patch 1: Comment out Windows platform check
    pattern = r"if sys\.platform == 'win32':\s+raise NotImplementedError\('Windows platform not yet working for Android'\)"
    if re.search(pattern, content):
        content = re.sub(
            pattern,
            "# Patched: Allow Windows platform\n# if sys.platform == 'win32':\n#     raise NotImplementedError('Windows platform not yet working for Android')",
            content
        )
        if content != original_content:
            patches_applied.append("Windows platform check disabled")
            original_content = content

    # Patch 2: Fix _winreg import for Python 3
    pattern = r"import _winreg"
    if re.search(pattern, content):
        content = re.sub(
            pattern,
            "import winreg as _winreg  # Patched: Python 3 compatibility",
            content
        )
        if content != original_content:
            patches_applied.append("_winreg import fixed for Python 3")
            original_content = content

    # Patch 3: Fix distutils import for Python 3.12+
    pattern = r"^from distutils\.version import LooseVersion$"
    if re.search(pattern, content, re.MULTILINE):
        replacement = """try:
    from distutils.version import LooseVersion
except ImportError:
    from packaging.version import Version as LooseVersion  # Python 3.12+"""
        content = re.sub(pattern, replacement, content, count=1, flags=re.MULTILINE)
        if content != original_content:
            patches_applied.append("distutils import fixed for Python 3.12+")
            original_content = content

    # Patch 4: Fix git config command output handling for Windows
    # Match the full multi-line cur_url assignment
    pattern = r'cur_url = cmd\(\s*\["git", "config", "--get", "remote\.origin\.url"\],\s*get_stdout=True,\s*cwd=p4a_dir,\s*\)\[0\]\.strip\(\)'
    if re.search(pattern, content, re.DOTALL):
        replacement = '''result = cmd(
                    ["git", "config", "--get", "remote.origin.url"],
                    get_stdout=True,
                    cwd=p4a_dir,
                )
                cur_url = result[0].strip() if result and result[0] else None
                if not cur_url:  # If git config fails, assume it's a fresh install
                    continue'''
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        if content != original_content:
            patches_applied.append("git config output handling fixed")
            original_content = content

    # Patch 5: Fix PATH separator in check_requirements - use os.pathsep instead of ':'
    pattern = r"self\.buildozer\.environ\['PATH'\] = ':'.join\(path\)"
    if re.search(pattern, content):
        # Import os at the top if not already imported
        if "import os\n" not in content[:1000]:
            content = re.sub(r"(import sys\n)", r"\1import os\n", content, count=1)
        content = re.sub(
            pattern,
            "self.buildozer.environ['PATH'] = os.pathsep.join(path)  # Patched: use os.pathsep for cross-platform",
            content
        )
        if content != original_content:
            patches_applied.append("PATH separator fixed in check_requirements")
            original_content = content

    if patches_applied:
        with open(android_py, 'w', encoding='utf-8') as f:
            f.write(content)
        return patches_applied
    return []

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python patch_buildozer.py <path_to_buildozer_init.py>")
        sys.exit(1)

    init_file = sys.argv[1]
    targets_dir = os.path.join(os.path.dirname(init_file), 'targets')

    all_patches = []

    # Patch __init__.py
    patches = patch_buildozer_init(init_file)
    if patches:
        all_patches.extend(patches)
        print(f"[OK] Patched __init__.py: {', '.join(patches)}")

    # Patch android.py
    patches = patch_android_target(targets_dir)
    if patches:
        all_patches.extend(patches)
        print(f"[OK] Patched android.py: {', '.join(patches)}")

    if all_patches:
        print(f"[OK] Successfully applied {len(all_patches)} patch(es)")
        sys.exit(0)
    else:
        print("[WARN] No patches were applied")
        sys.exit(1)

