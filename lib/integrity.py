import hashlib


def sha256(input_data):
    if isinstance(input_data, bytes):
        return hashlib.sha256(input_data).hexdigest()
    return hashlib.sha256(str(input_data).encode("utf-8")).hexdigest()


def build_custody_entry(*, label, type_, hash_, ingested_at):
    return {
        "label": label,
        "type": type_,
        "sha256": hash_,
        "ingestedAt": ingested_at,
        "status": "verified-from-intake",
    }
