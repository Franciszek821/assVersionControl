import os
import hashlib
import zipfile
import zlib
import time
import difflib
import shutil

from assvcPackage.utils import find_assvc, get_ignore
from assvcPackage.reverse import reverse




def comImport(zip_path):
    try:
        if not os.path.isfile(zip_path):
            print(f"Error: The file '{zip_path}' does not exist.")
            return
        
        if os.path.exists('.assvc'):
            print(f"Error: The directory .assvc already exists.")
            return
        
        print("IMPORTING FROM:", zip_path)
        try:
            os.mkdir(".assvc")
        except OSError:
            print("Error: Could not create .assvc directory.")
            return
        
        try:
            decompress_zip(zip_path)
        except Exception:
            print("Error: Failed to decompress repository data.")
            try:
                shutil.rmtree(".assvc")
            except:
                pass
            return
        
        try:
            reverse(commit_sha="latest", isPrintArgument=False, isForce=True)
        except Exception:
            print("Error: Failed to restore repository state.")
            return
        
        print("Import complete!")
    except Exception:
        print("Error: An unexpected error occurred during import.")

def comExport():
    try:
        assvc_path = find_assvc()
        if not assvc_path:
            print("Error: .assvc directory not found. Not an assvc repository.")
            return
        
        parent_path = os.path.dirname(assvc_path)
        ignore_dirs, ignore_files = get_ignore(parent_path)

        parentname = os.path.basename(parent_path)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        export_dir = f"assvc_{parentname}"
        print("EXPORTING TO FOLDER:", export_dir)
        
        try:
            compress_directory_to_zip(assvc_path, f"{export_dir}.zip")
            print("Compression complete!")
        except Exception:
            print("Error: Failed to create export file.")
    except Exception:
        print("Error: An unexpected error occurred during export.")

def compress_directory_to_zip(source_dir, output_zip):
    try:
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    try:
                        full_path = os.path.join(root, file)
                        relative_path = os.path.relpath(full_path, source_dir)
                        zipf.write(full_path, relative_path)
                    except Exception:
                        print(f"Warning: Could not add {file} to archive")
    except IOError:
        raise Exception(f"Cannot write to {output_zip}")
    except zipfile.BadZipFile:
        raise Exception("Error creating ZIP file")

def decompress_zip(zip_path):
    try:
        extract_to = os.getcwd()
        extract_to = os.path.join(extract_to, ".assvc")
        
        if not zipfile.is_zipfile(zip_path):
            raise Exception("Not a valid ZIP file")
        
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(extract_to)
        print(f"Decompressed '{zip_path}' to '{extract_to}'")
    except zipfile.BadZipFile:
        raise Exception("Corrupted ZIP file")
    except IOError:
        raise Exception("Cannot read ZIP file")
    except Exception as e:
        raise
