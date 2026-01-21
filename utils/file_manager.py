import os
import hashlib

def get_file_hash(filepath):
    """Calculate MD5 hash of a file."""
    hasher = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            buf = f.read(65536)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(65536)
        return hasher.hexdigest()
    except Exception:
        return None

def remove_duplicates(directory):
    """
    Scans the directory for duplicate files.
    Retains the first occurrence, removes subsequent duplicates.
    Returns a list of removed files.
    """
    unique_hashes = {}
    removed_files = []
    
    if not os.path.exists(directory):
        return []
    
    for root, dirs, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_hash = get_file_hash(filepath)
            
            if not file_hash:
                continue
                
            if file_hash in unique_hashes:
                # Duplicate found
                try:
                    os.remove(filepath)
                    removed_files.append(filename)
                except Exception:
                    pass
            else:
                unique_hashes[file_hash] = filepath
                
    return removed_files
