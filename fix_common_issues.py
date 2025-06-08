#!/usr/bin/env python
"""
Fix common Django setup issues
"""
import os
import sys
from pathlib import Path

def fix_line_endings(file_path):
    """Fix line endings in Python files"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace various line endings with Unix style
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Fix common issues in the Django project"""
    print("🔧 Fixing common Django setup issues...")
    
    project_root = Path(__file__).resolve().parent
    parts_interchange_dir = project_root / 'parts_interchange'
    
    # Files to check and fix
    critical_files = [
        parts_interchange_dir / 'apps' / 'parts' / 'views_fast.py',
        parts_interchange_dir / 'apps' / 'parts' / 'urls.py',
        parts_interchange_dir / 'apps' / 'parts' / 'models.py',
        parts_interchange_dir / 'apps' / 'parts' / 'admin.py',
        parts_interchange_dir / 'parts_interchange' / 'settings.py',
        parts_interchange_dir / 'parts_interchange' / 'urls.py',
    ]
    
    print("1. Fixing line endings in critical files...")
    for file_path in critical_files:
        if file_path.exists():
            if fix_line_endings(file_path):
                print(f"   ✅ Fixed: {file_path.name}")
            else:
                print(f"   ❌ Failed: {file_path.name}")
        else:
            print(f"   ⚠️  Not found: {file_path}")
    
    print("2. Creating missing __init__.py files...")
    init_files = [
        parts_interchange_dir / 'apps' / '__init__.py',
        parts_interchange_dir / 'apps' / 'parts' / '__init__.py',
        parts_interchange_dir / 'apps' / 'vehicles' / '__init__.py',
        parts_interchange_dir / 'apps' / 'fitments' / '__init__.py',
        parts_interchange_dir / 'apps' / 'api' / '__init__.py',
        parts_interchange_dir / 'apps' / 'parts' / 'management' / '__init__.py',
        parts_interchange_dir / 'apps' / 'parts' / 'management' / 'commands' / '__init__.py',
    ]
    
    for init_file in init_files:
        if not init_file.exists():
            init_file.parent.mkdir(parents=True, exist_ok=True)
            init_file.write_text('')
            print(f"   ✅ Created: {init_file}")
        else:
            print(f"   ✅ Exists: {init_file.name}")
    
    print("3. Checking Python path setup...")
    sys.path.insert(0, str(parts_interchange_dir))
    print(f"   ✅ Added to Python path: {parts_interchange_dir}")
    
    print("\n✅ Common issues fixed!")
    print("Now try running: python verify_setup.py")

if __name__ == '__main__':
    main()
