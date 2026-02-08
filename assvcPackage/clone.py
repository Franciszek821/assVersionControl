import os
import hashlib
import zipfile
import zlib
import time
import difflib
import shutil
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from warning import show_warning

from assvcPackage.utils import find_assvc, get_ignore
from assvcPackage.reverse import reverse




def comImport(zip_path):
    try:
        if not os.path.isfile(zip_path):
            show_warning(None, "File Error", f"The file '{zip_path}' does not exist.")
            return
        
        if os.path.exists('.assvc'):
            show_warning(None, "Directory Error", "The directory .assvc already exists.")
            return
        
        print("IMPORTING FROM:", zip_path)
        try:
            os.mkdir(".assvc")
        except OSError:
            show_warning(None, "Create Error", "Could not create .assvc directory.")
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
            show_warning(None, "Restore Error", "Failed to restore repository state.")
            return
        
        print("Import complete!")
    except Exception:
        show_warning(None, "Import Error", "An unexpected error occurred during import.")

def comExport(save_path=None, repo_path=None):
    try:
        # Change to repo directory if specified
        original_cwd = os.getcwd()
        if repo_path is not None:
            os.chdir(repo_path)
        
        try:
            assvc_path = find_assvc()
            if not assvc_path:
                show_warning(None, "Repository Error", ".assvc directory not found. Not an assvc repository.")
                return
            
            parent_path = os.path.dirname(assvc_path)
            ignore_dirs, ignore_files = get_ignore(parent_path)

            parentname = os.path.basename(parent_path)
            timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
            export_filename = f"assvc_{parentname}_{timestamp}.zip"
            
            # Use specified save path or original working directory
            if save_path is None:
                output_path = os.path.join(original_cwd, export_filename)
            else:
                output_path = os.path.join(save_path, export_filename)
            
            print("EXPORTING TO ZIP:", output_path)
            
            try:
                compress_directory_to_zip(assvc_path, output_path)
                print("Compression complete!")
            except Exception as e:
                show_warning(None, "Export Error", "Failed to create export file.", exception=e)
        finally:
            os.chdir(original_cwd)
    except Exception as e:
        show_warning(None, "Export Error", "An unexpected error occurred during export.", exception=e)

def compress_directory_to_zip(source_dir, output_zip):
    try:

        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    try:
                        full_path = os.path.join(root, file)
                        relative_path = os.path.relpath(full_path, source_dir)
                        zipf.write(full_path, relative_path)
                    except Exception as e:
                        show_warning(None, "Archive Warning", f"Could not add {file} to archive: {e}")

    except IOError as e:
        show_warning(None, f"Cannot write to {output_zip}", exception=e)
    except zipfile.BadZipFile as e:
        show_warning(None, "Error creating ZIP file", exception=e)

def decompress_zip(zip_path):
    try:
        extract_to = os.getcwd()
        extract_to = os.path.join(extract_to, ".assvc")
        
        if not zipfile.is_zipfile(zip_path):
            show_warning(None, "Not a valid ZIP file")
        
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(extract_to)
        print(f"Decompressed '{zip_path}' to '{extract_to}'")
    except zipfile.BadZipFile as e:
        show_warning(None, "Corrupted ZIP file", exception=e)
    except IOError as e:
        show_warning(None, "Cannot read ZIP file", exception=e)
    except Exception as e:
        show_warning(None, "Decompression Error", "An unexpected error occurred during decompression.", exception=e)
