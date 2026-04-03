import hashlib

def generate_file_hash(file_bytes: bytes) -> str:
    """
    Generate SHA-256 hash of file bytes.
    """
    return hashlib.sha256(file_bytes).hexdigest()
