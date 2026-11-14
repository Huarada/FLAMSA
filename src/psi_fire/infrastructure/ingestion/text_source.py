"""Raw text decoding shared by every raw-file reader."""

FALLBACK_ENCODING = "cp1252"  # FLEX experimental table is not UTF-8 (ADR-0013)


def decode(data: bytes) -> tuple[str, str]:
    try:
        return data.decode("utf-8-sig"), "utf-8"
    except UnicodeDecodeError:
        return data.decode(FALLBACK_ENCODING), FALLBACK_ENCODING
