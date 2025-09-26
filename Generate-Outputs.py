import os
import subprocess
import shutil
from multiprocessing import Pool, cpu_count

# ==============================================================================
#                                 Settings
# ==============================================================================

PROJECT_NAME = "advanced" 
ROOT_DIR = os.getcwd()
OUTPUTS_DIR = os.path.join(ROOT_DIR, "Outputs")

# --- Cleanup Logic ---
if os.path.exists(OUTPUTS_DIR):
    print(f"[CLEANUP] Removing old '{os.path.relpath(OUTPUTS_DIR, ROOT_DIR)}' directory...")
    shutil.rmtree(OUTPUTS_DIR)

os.makedirs(OUTPUTS_DIR)
print(f"[CLEANUP] Created a fresh '{os.path.relpath(OUTPUTS_DIR, ROOT_DIR)}' directory.")


# ==============================================================================
#                         Processing Function for a Single File
# ==============================================================================
def process_ctx_file(dirpath):
    """
    Compiles a single main.ctx file found in dirpath, and copies the
    resulting PDF to the Outputs directory. Returns a status message.
    """
    relative_dir = os.path.relpath(dirpath, ROOT_DIR)
    
    # Step 1: Run the 'context' command
    try:
        subprocess.run(
            ["context", "main.ctx"],
            cwd=dirpath,
            check=True,
            capture_output=True,
            text=True
        )
    except FileNotFoundError:
        return f"[FATAL ERROR] 'context' command not found. Is ConTeXt installed and in your PATH?"
    except subprocess.CalledProcessError:
        return f"[ERROR] Compilation failed for: {relative_dir}"

    # Step 2: Verify and get path for the created PDF
    pdf_path = os.path.join(dirpath, "main.pdf")
    if not os.path.exists(pdf_path):
        return f"[WARNING] 'main.pdf' not found after compilation in '{relative_dir}'. Skipping."

    # Step 3: Create a new, unique name for the PDF
    if relative_dir == ".":
        suffix = "root"
    else:
        suffix = "-".join(relative_dir.split(os.sep))
    
    new_pdf_name = f"{PROJECT_NAME}-{suffix}.pdf"

    # Step 4: Copy the final PDF to the Outputs directory
    final_pdf_path = os.path.join(OUTPUTS_DIR, new_pdf_name)
    shutil.copy(pdf_path, final_pdf_path)

    relative_final_path = os.path.relpath(final_pdf_path, ROOT_DIR)
    return f"[DONE] Successfully compiled {relative_dir} and saved as: {relative_final_path}"


# ==============================================================================
#                         Main Execution Logic
# ==============================================================================
if __name__ == "__main__":
    # --- Added separator after CLEANUP ---
    print("-" * 40)
    
    print(f"[START] Scanning for 'main.ctx' files in root directory...")

    # Phase 1: Collect all directories that contain a 'main.ctx' file
    ctx_directories = []
    for dirpath, dirnames, filenames in os.walk(ROOT_DIR):
        if os.path.commonpath([dirpath, OUTPUTS_DIR]) == OUTPUTS_DIR:
            continue
        if "main.ctx" in filenames:
            ctx_directories.append(dirpath)

    if not ctx_directories:
        print("\n[FINISH] No 'main.ctx' files were found to process.")
    else:
        num_files = len(ctx_directories)
        print(f"[INFO] Found {num_files} file(s) to process. Starting parallel compilation...")
        
        # --- Moved the separator here ---
        print("-" * 40)
        
        # Phase 2: Process the collected directories in parallel
        num_processes = cpu_count()
        print(f"[INFO] Using {num_processes} parallel processes.")
        
        # --- Added separator after process count ---
        print("-" * 40)

        with Pool(processes=num_processes) as pool:
            results = pool.map(process_ctx_file, ctx_directories)

        # Phase 3: Print the results from all processes
        # This separator was already here
        print("[RESULTS]")
        for res in results:
            print(res)

        print(f"\n[FINISH] All {num_files} file(s) processed. Check the '{os.path.relpath(OUTPUTS_DIR, ROOT_DIR)}' directory.")

