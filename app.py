import eel
from extractor import index_files, save_files, search_files
import os
import json

eel.init('web')  # Assuming your HTML/CSS/JS files are in a directory named 'web'

@eel.expose
def process_files(path, pattern):
    index_file_path = "./data/index.json"  # Adjust path for Eel

    # Function to check if the search path is within the indexed path
    def needs_indexing(search_path):
        try:
            with open(index_file_path, 'r') as file:
                data = json.load(file)
                # Now expecting a single string for the indexed path
                indexed_path = data.get("indexed_path", "")
                # Direct comparison or more complex logic to determine if re-indexing is needed
                return not search_path.startswith(indexed_path)
        except (json.JSONDecodeError, FileNotFoundError):
            return True  # Needs indexing if file is missing or corrupted

    if needs_indexing(path):
        eel.printToConsole("Index file is outdated or doesn't cover the path. Re-indexing...")
        files = index_files(path, maxDepth=10)
        eel.printToConsole(f"Indexed {len(files)} files.")
        
        # Note the change here to pass indexed_path as a string
        save_success = save_files(files, index_file_path, path)
        if save_success:
            eel.printToConsole("Files indexed and saved successfully.")
        else:
            eel.printToConsole("Failed to save the index file. Exiting...")
            return []

    # Proceed with searching within the updated or existing index
    matched_files = search_files(pattern, index_file_path)
    if matched_files:
        return matched_files
    else:
        eel.printToConsole("No files matched or an error occurred.")
        return []

@eel.expose
def update_index():
    try:
        with open("./data/index.json", 'r') as file:
            data = json.load(file)
            indexed_path = data.get("indexed_path", "")
            if indexed_path:
                eel.printToConsole(f"Updating index for path: {indexed_path}")
                files = index_files(indexed_path, maxDepth=10)
                save_success = save_files(files, "./data/index.json", indexed_path)
                if save_success:
                    eel.printToConsole("Index updated successfully.")
                else:
                    eel.printToConsole("Failed to update the index.")
            else:
                eel.printToConsole("No indexed path found for updating.")
    except Exception as e:
        eel.printToConsole(f"Error updating index: {e}")


eel.start('index.html', size=(800, 600))
