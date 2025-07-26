import os
import zipfile
import shutil

# Define base paths
root_dir = os.path.abspath(".")
output_dir = os.path.join(root_dir, "blender_addon")
addon_name = "r3f_exporter"
addon_folder = os.path.join(output_dir, addon_name)
zip_path = os.path.join(output_dir, f"{addon_name}.zip")

# Clean previous build
if os.path.exists(addon_folder):
    shutil.rmtree(addon_folder, ignore_errors=True)
if os.path.exists(zip_path):
    os.remove(zip_path)

# Create addon folder
os.makedirs(addon_folder, exist_ok=True)

# Copy files into addon_folder
for foldername, subfolders, filenames in os.walk(root_dir):
    if any(ignored in foldername for ignored in ["node_modules", "blender_addon", ".git"]):
        continue

    for filename in filenames:
        if filename.endswith(".zip") or filename == "zipper.py":
            continue

        src_path = os.path.join(foldername, filename)
        rel_path = os.path.relpath(src_path, root_dir)
        dest_path = os.path.join(addon_folder, rel_path)

        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copy2(src_path, dest_path)

# Zip the addon folder
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
    for foldername, _, filenames in os.walk(addon_folder):
        for filename in filenames:
            file_path = os.path.join(foldername, filename)
            arcname = os.path.relpath(file_path, output_dir)  # includes addon folder in archive
            zipf.write(file_path, arcname)

# Safely remove addon folder
shutil.rmtree(addon_folder, ignore_errors=True)
print(f"✅ Project zipped to {zip_path} and cleaned up.")
