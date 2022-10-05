import os
import sys

# add git submodule to path to allow imports to work
# credits to https://stackoverflow.com/a/29747054 and https://stackoverflow.com/a/73885828
submodule_name = "docs/assets/import_scripts"
(parent_folder_path, current_dir) = os.path.split(os.path.dirname(__file__))
sys.path.append(os.path.join(parent_folder_path, submodule_name))
