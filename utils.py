# utils.py
import os
import zipfile
import py7zr

def compress_to_zip(file_paths, output_path):
    """Compress a list of files into a zip archive."""
    with zipfile.ZipFile(output_path, 'w') as zipf:
        for file in file_paths:
            zipf.write(file, os.path.basename(file))

def compress_to_7zip(file_paths, output_path):
    """Compress a list of files into a 7zip archive."""
    with py7zr.SevenZipFile(output_path, 'w') as seven_zip:
        for file in file_paths:
            seven_zip.write(file, os.path.basename(file))

def cleanup_temp_dir(dir_path):
    """Clean up a temporary directory."""
    for root, dirs, files in os.walk(dir_path, topdown=False):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs:
            os.rmdir(os.path.join(root, dir))
    os.rmdir(dir_path)