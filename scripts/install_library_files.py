# Used in Arduino / ESP / STM32 / Pico GitHub workflows (inline or as script).
# Env: LIBRARY_FILES = workflow input library_files (JSON array)

import base64
import json
import os
import shutil
import tempfile
import zipfile
from io import BytesIO

LIB_FILES_JSON = os.environ.get("LIBRARY_FILES", "") or os.environ.get("library_files", "")


def _install_zip_bytes(data: bytes, zip_label: str, libs_dir: str) -> None:
    zip_label = (zip_label or "CustomLib").strip() or "CustomLib"

    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(BytesIO(data)) as zf:
            zf.extractall(tmp)
        entries = [e for e in os.listdir(tmp) if not e.startswith(".")]

        # Standard Arduino zip: one root folder (MyLib/MyLib.h) -> use inner folder name.
        if len(entries) == 1 and os.path.isdir(os.path.join(tmp, entries[0])):
            lib_name = entries[0]
            root = os.path.join(tmp, lib_name)
        else:
            # Flat zip or multiple root entries: install under zip file name.
            lib_name = zip_label
            root = tmp

        target = os.path.join(libs_dir, lib_name)
        os.makedirs(target, exist_ok=True)
        for item_name in os.listdir(root):
            src = os.path.join(root, item_name)
            dst = os.path.join(target, item_name)
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
    print(f"Installed {lib_name}")


def install_uploaded_libraries() -> None:
    if not LIB_FILES_JSON.strip():
        print("library_files empty, skipping")
        return
    libs_dir = os.path.expanduser("~/Arduino/libraries")
    os.makedirs(libs_dir, exist_ok=True)
    items = json.loads(LIB_FILES_JSON)
    for item in items:
        zip_label = (item.get("name") or "CustomLib").strip()
        b64 = item.get("zip") or ""
        if not b64:
            continue
        data = base64.b64decode(b64)
        _install_zip_bytes(data, zip_label, libs_dir)


if __name__ == "__main__":
    install_uploaded_libraries()
