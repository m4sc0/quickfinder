import os
import json

def index_files(path, depth=1, maxDepth=10):
    fileList = []
    
    if depth > maxDepth:
        return fileList

    try:
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            if os.path.isfile(full_path):
                fileList.append({"name": item, "path": full_path, "size": os.path.getsize(full_path), "last_modified": os.path.getmtime(full_path)})
            elif os.path.isdir(full_path):
                fileList.extend(index_files(full_path, depth + 1, maxDepth))
    except Exception as e:
        print(f"Error accessing '{path}': {e}. Skipping...")

    return fileList

def save_files(files, path="./index.json", indexed_path=""):
    data = {
        "indexed_path": indexed_path,
        "files": files
    }
    try:
        if not os.path.exists(path):
            os.mkdir(os.path.dirname(path))
        with open(path, 'w') as file:
            json.dump(data, file, indent=2)
            return True
    except Exception as e:
        print(f"Error saving file '{path}': {e}")
        return False

def search_files(pattern, path="./index.json"):
    try:
        result = []
        with open(path, 'r') as file:
            data = json.load(file)
            result = [entry for entry in data.get('files', []) if pattern.lower() in entry['name'].lower()]
        
        return result
    except Exception as e:
        print(f"Error searching in file '{path}': {e}")
        return False
