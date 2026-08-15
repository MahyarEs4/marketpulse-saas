import os

def print_tree(root="."):
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip hidden and venv folders
        dirnames[:] = [d for d in dirnames if not d.startswith('.') and d not in ('venv', '__pycache__', 'node_modules', '.git')]
        level = dirpath.replace(root, '').count(os.sep)
        indent = '  ' * level
        print(f"{indent}{os.path.basename(dirpath)}/")
        for f in filenames:
            print(f"{'  ' * (level+1)}{f}")

print_tree(".")
