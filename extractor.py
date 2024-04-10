import os
import json
import psutil

def get_partitions():
    partitions = []
    for part in psutil.disk_partitions():
        if 'cdrom' in part.opts or part.fstype == '':
            continue
        partitions.append(part.mountpoint)
    return partitions

def index_files(search_pattern=None, maxDepth=10):
    fileList = []
    paths = get_partitions()

    def _index_files(path, depth=1):
        if depth > maxDepth:
            return
        try:
            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                data = {
                    "name": item,
                    "path": full_path,
                    "size": os.path.getsize(full_path),
                    "type": "dir" if os.path.isdir(full_path) else "file",
                    "last_modified": os.path.getmtime(full_path)
                }
                if search_pattern and search_pattern.lower() not in item.lower():
                    continue
                fileList.append(data)
                if data["type"] == "dir":
                    _index_files(full_path, depth + 1)
        except Exception as e:
            print(f"Error accessing '{path}': {e}. Skipping...")
    
    for path in paths:
        _index_files(path)
    return fileList

def save_files(files, path="./data/index.json", indexed_partitions=[]):
    data = {
        "indexed_partitions": indexed_partitions,
        "files": files
    }
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as file:
            json.dump(data, file, indent=2)
            return True
    except Exception as e:
        print(f"Error saving file '{path}': {e}")
        return False
