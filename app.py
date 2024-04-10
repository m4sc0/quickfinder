import eel
from extractor import index_files, save_files, get_partitions
import os
import json
import subprocess
import platform

eel.init('web')

# Globaler Speicher für den Index
loaded_index = {}

@eel.expose
def load_index_into_memory():
    global loaded_index
    index_file_path = "./data/index.json"
    try:
        with open(index_file_path, 'r') as file:
            loaded_index = json.load(file)
            print("Index successfully loaded into memory.")
    except Exception as e:
        print(f"Failed to load index into memory: {e}")

@eel.expose
def search_files(pattern, use_index=True):
    global loaded_index
    files = []
    if use_index:
        try:
            files = [f for f in loaded_index.get('files', []) if pattern.lower() in f['name'].lower()]
            eel.printToConsole(f"Found {len(files)} files in index matching '{pattern}'.")
        except Exception as e:
            eel.printToConsole(f"Error searching index in memory: {e}")
            files = []
    else:
        eel.printToConsole("Indexing and searching the entire filesystem. This may take a while...")
        all_partitions = get_partitions()
        files = index_files(search_pattern=pattern)
        # Nach der direkten Suche den Index aktualisieren, sowohl im Speicher als auch auf der Festplatte
        loaded_index = {'files': files}
        index_file_path = "./data/index.json"
        save_files(files, index_file_path)  # Optionally save the results for future
    return files

@eel.expose
def update_index(callback = None):
    global loaded_index
    index_file_path = "./data/index.json"
    partitions = get_partitions()
    eel.printToConsole("Updating index for the entire filesystem. This may take a while...")
    files = index_files()
    loaded_index = {'files': files}  # Update den Index im Speicher
    save_success = save_files(files, index_file_path, partitions)
    if save_success:
        eel.printToConsole("Index updated successfully.")
    else:
        eel.printToConsole("Failed to update the index.")
    callback()

@eel.expose
def open_file_or_directory(path):
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", path], check=True)
        else:  # Linux und andere Unix-ähnliche Systeme
            subprocess.run(["xdg-open", path], check=True)
    except Exception as e:
        eel.printToConsole(f"Error opening file or directory: {e}")

eel.start('index.html', size=(900, 600), )