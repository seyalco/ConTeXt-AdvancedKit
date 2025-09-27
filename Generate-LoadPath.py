import os

def create_search_path_file(root_path, main_ctx_dir):
    # ... (docstring remains the same) ...
    r"""
    Finds all relevant search paths for a given main.ctx file, formats them
    as TeX \usepath commands relative to the main.ctx location, and writes
    them to a PathList.ctx file.

    The paths include:
    1. 'Common-*' directories on the path from the current directory up to the root,
       AND ALL THEIR SUBDIRECTORIES recursively (excluding 'Backups').
    2. All subdirectories within the same folder as main.ctx (excluding 'Backups').
    3. All parent directories from the main.ctx folder up to the root.
    
    The path of main.ctx itself is excluded from the output.
    
    At the end, it adds a \setupexternalfigures command containing all found paths.
    """
    # --- Part 0: Initial Setup ---
    abs_root_path = os.path.abspath(root_path)
    abs_main_ctx_dir = os.path.abspath(main_ctx_dir)
    search_paths_abs = set()
    common_excluded_folder = "Backups"

    # --- Part 1: Find 'Common-*' directories and ALL their subdirectories ---
    current_path_part_for_common = abs_main_ctx_dir
    while True:
        try:
            items = os.listdir(current_path_part_for_common)
        except FileNotFoundError:
            break

        for item in items:
            item_path = os.path.join(current_path_part_for_common, item)
            if os.path.isdir(item_path) and item.startswith("Common-"):
                for dirpath, dirnames, _ in os.walk(item_path, topdown=True):
                    if common_excluded_folder in dirnames:
                        dirnames.remove(common_excluded_folder)
                    search_paths_abs.add(os.path.abspath(dirpath))

        if os.path.samefile(current_path_part_for_common, abs_root_path):
            break
        current_path_part_for_common = os.path.dirname(current_path_part_for_common)

    # --- Part 2: Find all local subdirectories ---
    local_excluded_folder = "Backups"
    for dirpath, dirnames, _ in os.walk(abs_main_ctx_dir, topdown=True):
        if local_excluded_folder in dirnames:
            dirnames.remove(local_excluded_folder)
        search_paths_abs.add(os.path.abspath(dirpath))

    # --- Part 3: Add all parent directories up to the root ---
    current_path_part_for_parents = abs_main_ctx_dir
    while not os.path.samefile(current_path_part_for_parents, abs_root_path):
        parent_dir = os.path.dirname(current_path_part_for_parents)
        search_paths_abs.add(os.path.abspath(parent_dir))
        if os.path.samefile(parent_dir, abs_root_path):
            break
        current_path_part_for_parents = parent_dir
    
    # --- Part 4: Process and write the output file ---
    # --- MODIFICATION STARTS HERE ---

    if abs_main_ctx_dir in search_paths_abs:
        search_paths_abs.remove(abs_main_ctx_dir)

    if not search_paths_abs:
        # If there are no paths to write, do nothing.
        # This avoids creating an empty or incomplete file.
        print(f"No search paths found for {os.path.relpath(main_ctx_dir, root_path)}. No file created.")
        return

    # Calculate paths relative to main_ctx_dir
    relative_paths = []
    for abs_path in search_paths_abs:
        rel_path = os.path.relpath(abs_path, start=abs_main_ctx_dir)
        rel_path_posix = rel_path.replace(os.sep, '/')
        # For \setupexternalfigures, '.' is better than an empty string.
        # But let's handle the empty string case for \usepath later.
        relative_paths.append(rel_path_posix)

    sorted_paths = sorted(relative_paths)
    
    output_file_path = os.path.join(main_ctx_dir, "PathList.ctx")
    relative_output_path_to_root = os.path.relpath(output_file_path, root_path).replace(os.sep, '/')

    with open(output_file_path, 'w', encoding='utf-8') as f:
        # Step 1: Write all the \usepath commands
        for path in sorted_paths:
            # For \usepath[{}], an empty string is used for the current directory.
            path_to_write_usepath = path if path != '.' else ''
            f.write(f"\\usepath[{{{path_to_write_usepath}}}]\n")
        
        # Add a blank line for better readability
        f.write("\n")

        # Step 2: Create the comma-separated list for \setupexternalfigures
        # For this command, the standard '.' is fine for the current directory.
        # The list 'sorted_paths' already contains '.' where needed.
        # Example: ['..', '../../Common-Setups', 'Setups']
        comma_separated_paths = ",".join(sorted_paths)
        
        # Step 3: Write the \setupexternalfigures command
        f.write(f"\\setupexternalfigures[directory={{{comma_separated_paths}}}]\n")
    
    print(f"Successfully created/updated: {relative_output_path_to_root}")
    # --- MODIFICATION ENDS HERE ---


def main():
    # ... (main function remains unchanged) ...
    try:
        root_directory = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        root_directory = os.getcwd()

    print(f"Project Root: {root_directory}\n")
    
    root_excluded_folder = "Backups"

    for dirpath, dirnames, filenames in os.walk(root_directory, topdown=True):
        if root_excluded_folder in dirnames and os.path.samefile(dirpath, root_directory):
            dirnames.remove(root_excluded_folder)

        if "main.ctx" in filenames:
            create_search_path_file(root_directory, dirpath)

if __name__ == "__main__":
    main()

