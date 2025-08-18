def fileSafe(text):
    safe_text = "".join(c if c.isalnum() or c in " _-" else "_" for c in text)
    return safe_text
