from pathlib import Path

def get_next_test_output_filename(base_name: str, extension: str, output_dir: Path = Path("output")) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    index = 1
    while True:
        filename = output_dir / f"test{index}_{base_name}.{extension}"
        if not filename.exists():
            return filename
        index += 1