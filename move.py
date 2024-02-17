import os
import shutil
from difflib import SequenceMatcher

# Paths to the old and new QMK firmware repositories
old_repo_path = '../qmk_firmware_fcoury'
new_repo_path = '../qmk_firmware'

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

# Function to recursively find all instances of mrkeebs keymaps in the old repo
def find_mrkeebs_keymaps(directory):
    mrkeebs_keymaps = []
    for root, _, _ in os.walk(directory):
        if root.endswith('keymaps/mrkeebs'):
            mrkeebs_keymaps.append(root)
    return mrkeebs_keymaps

# Search for a keyboard in the new repository by name
def search_for_keyboard_in_new_repo(keyboard_name):
    best_match = (None, 0)  # (path, similarity_score)
    for root, dirs, _ in os.walk(os.path.join(new_repo_path, 'keyboards')):
        for dir in dirs:
            current_similarity = similarity(keyboard_name, dir)
            if current_similarity > best_match[1]:
                best_match = (os.path.join(root, dir), current_similarity)
    return best_match[0] if best_match[1] > 0.3 else None  # Only return matches above a certain threshold

# Copy the keymaps and handle non-matches with search, and skip if exists
def copy_keymaps_and_handle_non_matches(keymaps):
    for keymap_path in keymaps:
        relative_path = os.path.relpath(keymap_path, old_repo_path)
        new_keymap_path = os.path.join(new_repo_path, relative_path)
        
        if os.path.exists(new_keymap_path):
            print(f"Keymap already exists, skipping: {new_keymap_path}")
            continue
        
        if os.path.exists(os.path.dirname(new_keymap_path)):
            shutil.copytree(keymap_path, new_keymap_path, dirs_exist_ok=True)
            print(f"Copied keymap: {relative_path}")
        else:
            keyboard_name = "/".join(relative_path.split('/')[1:-2])  # Get the keyboard's path excluding 'keymaps/mrkeebs'
            new_keyboard_path = search_for_keyboard_in_new_repo(keyboard_name)
            if new_keyboard_path:
                proposed_new_keymap_path = os.path.join(new_keyboard_path, 'keymaps', 'mrkeebs')
                print(f"Potential new location found for {keyboard_name}: {new_keyboard_path}")
                confirm = input(f"Do you want to copy the keymap from '{relative_path}' to '{proposed_new_keymap_path}'? [y/N]: ")
                if confirm.lower() == 'y':
                    if not os.path.exists(proposed_new_keymap_path):
                        os.makedirs(proposed_new_keymap_path)
                    shutil.copytree(keymap_path, proposed_new_keymap_path, dirs_exist_ok=True)
                    print(f"Copied keymap to new location: {proposed_new_keymap_path}")
            else:
                print(f"Non-matching keymap (keyboard not found in new repo): {relative_path}")

# Find all mrkeebs keymaps in the old repository
mrkeebs_keymaps = find_mrkeebs_keymaps(os.path.join(old_repo_path, 'keyboards'))

# Copy the keymaps and handle the non-matching ones with potential search and confirmation, skipping existing keymaps
copy_keymaps_and_handle_non_matches(mrkeebs_keymaps)

