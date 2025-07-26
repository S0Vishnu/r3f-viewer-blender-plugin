import os
import zipfile

# Define paths
root_dir = os.path.abspath(".")
output_dir = os.path.join(root_dir, "blender_addon")
zip_path = os.path.join(output_dir, "r3f_exporter.zip")

# Ensure output folder exists
os.makedirs(output_dir, exist_ok=True)

# Remove existing zip file if present
if os.path.exists(zip_path):
    os.remove(zip_path)
    print(f"🗑️ Removed existing zip: {zip_path}")

# Create ZIP
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
    for foldername, subfolders, filenames in os.walk(root_dir):
        # Skip undesired folders
        if "node_modules" in foldername or "blender_addon" in foldername:
            continue
        for filename in filenames:
            if filename.endswith(".zip") or filename == "zipper.py":
                continue
            file_path = os.path.join(foldername, filename)
            arcname = os.path.relpath(file_path, root_dir)
            zipf.write(file_path, arcname)

print(f"✅ Project zipped to {zip_path}")
