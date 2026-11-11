import base64
import hashlib
import hmac
import json
import secrets
import struct
import time
from typing import List, Optional, Tuple
from urllib.parse import quote

from reportlab.graphics import renderSVG
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing


def generate_totp_secret(length_bytes: int = 20) -> str:
    """Genera un secreto aleatorio en Base32 (sin padding '=') compatible con Google/Microsoft Authenticator."""
    raw = secrets.token_bytes(length_bytes)
    return base64.b32encode(raw).decode("ascii").rstrip("=")


def _normalize_base32_secret(secret: str) -> bytes:
    cleaned = "".join((secret or "").strip().split()).upper()
    missing_padding = len(cleaned) % 8
    if missing_padding:
        cleaned += "=" * (8 - missing_padding)
    return base64.b32decode(cleaned, casefold=True)


def generate_totp_code(
    secret: str,
    for_time: Optional[int] = None,
    interval: int = 30,
    digits: int = 6,
) -> str:
    """Calcula el código TOTP RFC 6238 de 6 dígitos para el instante indicado."""
    if for_time is None:
        for_time = int(time.time())
    key = _normalize_base32_secret(secret)
    counter = int(for_time // interval)
    msg = struct.pack(">Q", counter)
    digest = hmac.new(key, msg, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code_int = (struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7FFFFFFF) % (10 ** digits)
    return str(code_int).zfill(digits)


def verify_totp_code(
    secret: str,
    code: str,
    window: int = 1,
    interval: int = 30,
    digits: int = 6,
) -> bool:
    """Verifica un código TOTP de 6 dígitos permitiendo ±window intervalos de 30s por desfase de reloj."""
    if not secret or not code:
        return False
    clean_code = "".join(ch for ch in str(code).strip() if ch.isdigit())
    if len(clean_code) != digits:
        return False
    try:
        now = int(time.time())
        for offset in range(-window, window + 1):
            candidate = generate_totp_code(
                secret,
                for_time=now + offset * interval,
                interval=interval,
                digits=digits,
            )
            if hmac.compare_digest(candidate, clean_code):
                return True
        return False
    except Exception:
        return False


def build_otpauth_uri(
    secret: str,
    account_name: str,
    issuer: str = "Pacific Forest Internacional",
) -> str:
    """Construye la URI otpauth://totp/... estándar para escanear en apps autenticadoras."""
    clean_issuer = (issuer or "Pacific Forest").strip()
    clean_account = (account_name or "usuario").strip()
    label = quote(f"{clean_issuer}:{clean_account}")
    issuer_param = quote(clean_issuer)
    return f"otpauth://totp/{label}?secret={secret}&issuer={issuer_param}&algorithm=SHA1&digits=6&period=30"


def generate_qr_svg_data_uri(data: str, size: int = 240) -> str:
    """Genera un código QR en formato SVG embebido en Data URI base64."""
    widget = qr.QrCodeWidget(data)
    bounds = widget.getBounds()
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    drawing = Drawing(
        size,
        size,
        transform=[size / float(width), 0, 0, size / float(height), 0, 0],
    )
    drawing.add(widget)
    svg_str = renderSVG.drawToString(drawing)
    encoded = base64.b64encode(svg_str.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def _hash_backup_code(code: str) -> str:
    normalized = "".join(ch for ch in (code or "").upper() if ch.isalnum())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def generate_backup_codes(count: int = 8) -> Tuple[List[str], str]:
    """Genera códigos de respaldo legibles (XXXX-XXXX) y devuelve la lista en texto plano + JSON de hashes."""
    alphabet = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
    plain_codes: List[str] = []
    hashed_codes: List[str] = []

    for _ in range(count):
        part1 = "".join(secrets.choice(alphabet) for _ in range(4))
        part2 = "".join(secrets.choice(alphabet) for _ in range(4))
        formatted = f"{part1}-{part2}"
        plain_codes.append(formatted)
        hashed_codes.append(_hash_backup_code(formatted))

    return plain_codes, json.dumps(hashed_codes)


def count_remaining_backup_codes(stored_json: Optional[str]) -> int:
    if not stored_json:
        return 0
    try:
        parsed = json.loads(stored_json)
        return len(parsed) if isinstance(parsed, list) else 0
    except Exception:
        return 0


def verify_and_consume_backup_code(
    stored_json: Optional[str],
    code: str,
) -> Tuple[bool, Optional[str]]:
    """Verifica si el código coincide con un código de respaldo disponible y lo consume (elimina)."""
    if not stored_json or not code:
        return False, stored_json
    try:
        hashes = json.loads(stored_json)
        if not isinstance(hashes, list) or not hashes:
            return False, stored_json
    except Exception:
        return False, stored_json

    candidate_hash = _hash_backup_code(code)
    matched_index = None
    for idx, stored_hash in enumerate(hashes):
        if isinstance(stored_hash, str) and hmac.compare_digest(stored_hash, candidate_hash):
            matched_index = idx
            break

    if matched_index is None:
        return False, stored_json

    remaining = [h for idx, h in enumerate(hashes) if idx != matched_index]
    return True, json.dumps(remaining)

