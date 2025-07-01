import magic
from pathlib import Path

def validate_mimetype(filename: str) -> str:
    path = Path(filename).resolve()
    mime = magic.Magic(mime=True)
    return mime.from_file(str(path))