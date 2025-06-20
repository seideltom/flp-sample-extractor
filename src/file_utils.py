import re
import os


def convert_binary_file_to_text(file_path):
    try:
        with open(file_path, 'rb') as f:
            data = f.read()

        # decode the binary data to text and replace null bytes
        text = data.decode('latin1', errors='ignore').replace('\x00', '')

    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        text = ""

    return text


def get_existing_unique_paths(text):

    # pattern for windows only
    pattern = r'([A-Z]:\\[^\n\r]*?\.(?:mp3|wav|ogg))'

    #pattern for linux and macOS only (loads extremly long when loading first files after startup)
    #pattern = r'/[^ \n\r]*?\.(?:mp3|wav|ogg)'
    
    #pattern for linux, windows and macOS (loads extremly long when loading first files after startup)
    #pattern = r'(' \
    #      r'(?:[A-Z]:\\[^\n\r]*?\.(?:mp3|wav|ogg))|' \
    #      r'(?:/[^ \n\r]*?\.(?:mp3|wav|ogg))' \
    #      r')'

    paths = re.findall(pattern, text)

    unique_paths = set(paths)

    existing_unique_paths = [path for path in unique_paths if os.path.exists(path)]

    return existing_unique_paths

def get_unique_destination_path(destination_folder, file_name):
    base_name, ext = os.path.splitext(file_name)
    counter = 1
    destination_path = os.path.join(destination_folder, file_name)

    # ensure that a new file is created instead of overwriting an existing one
    while os.path.exists(destination_path):
        new_file_name = f"{base_name} ({counter}){ext}"
        destination_path = os.path.join(destination_folder, new_file_name)
        counter += 1

    return destination_path