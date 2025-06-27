Thanks for sharing your updated sanitize and load functions! I see a few issues and suggestions to improve correctness and avoid errors:

Issues in your sanitize function
Line causing error:

python
Copy code
sanitized_filename = sanitized_stem / suffix
This is a bug — you are using the division operator / between two strings. In pathlib, / is overloaded for Path objects to join paths, not for strings.

You should concatenate strings here:

python
Copy code
sanitized_filename = sanitized_stem + suffix
Comparing filename (string) to sanitized_filename (Path or string):

You do:

python
Copy code
if filename != sanitized_filename:
But filename is the original input string (like "file.txt"), and sanitized_filename is either a string or Path (depending on above bug). Just ensure both are strings for comparison.

When creating new names with index:

python
Copy code
sanitized_path = Path(f"{sanitized_path_stem}_{index}{sanitized_path_suffix}")
This constructs a relative path without directory — consider if you want to keep it inside "inputs" folder:

python
Copy code
sanitized_path = semi_sanitized_path.parent / f"{sanitized_path_stem}_{index}{sanitized_path_suffix}"
Renaming the file:

python
Copy code
path.rename(sanitized_path.resolve())
Make sure the parent directory exists (you do that with mkdir), but also be aware rename() can fail if files are open or permissions lack.

Other minor suggestions
You might want to add .lower() to your suffix when checking ALLOWED_EXTENSIONS if it isn’t case-insensitive already.

The logging messages could be clearer about whether the renaming is due to invalid characters, file collision, or invalid extension.

Wrap path.rename() in try-except to catch potential OS errors and log them.

Corrected snippet for that key line:
python
Copy code
if suffix:
    if suffix not in ALLOWED_EXTENSIONS:
        raise InputError(f"ValidationError: '{suffix}' Not Accepted -- Exiting")
    sanitized_filename = sanitized_stem + suffix  # <- Use + here, not /
else:
    sanitized_filename = sanitized_stem
If you want, I can help you rewrite or test the whole function!



Ask ChatGPT
