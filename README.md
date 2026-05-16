# DirWatch

**DirWatch** is a minimal, single‑file Python utility that monitors a directory and prints a timestamped log whenever a file is created, modified, or deleted.

## Features
- Works on Windows, macOS, and Linux.
- No external dependencies – only the Python standard library.
- Idempotent: running the script repeatedly on the same path has no side effects.
- Clear, human‑readable output.

## Usage
```bash
python dirwatch.py /path/to/watch
```
The script will run until you interrupt it (Ctrl+C).

## How it works
It uses the `os` and `time` modules to periodically poll the directory contents, compare snapshots, and detect changes. The approach is deliberately simple to keep the code tiny and dependency‑free.

## License
This project is released into the public domain (Unlicense). Feel free to copy, modify, and distribute.
