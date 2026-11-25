import os
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

ALLOWED_RESUME_EXTENSIONS = ['pdf', 'doc', 'docx']
MAX_RESUME_SIZE_MB = 5
MAX_RESUME_SIZE_BYTES = MAX_RESUME_SIZE_MB * 1024 * 1024

# Standard file extension validator from Django
resume_extension_validator = FileExtensionValidator(
    allowed_extensions=ALLOWED_RESUME_EXTENSIONS,
    message=f"Unsupported file format. Only {', '.join(ALLOWED_RESUME_EXTENSIONS).upper()} files are permitted."
)

# Known file signatures (magic numbers) for verification
FILE_SIGNATURES = {
    'pdf': [b'%PDF-'],
    'doc': [b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'],
    'docx': [b'PK\x03\x04', b'PK\x05\x06', b'PK\x07\x08'],
}

ALLOWED_MIME_TYPES = {
    'pdf': ['application/pdf', 'application/x-pdf', 'application/octet-stream'],
    'doc': ['application/msword', 'application/vnd.ms-word', 'application/octet-stream'],
    'docx': [
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/zip',
        'application/x-zip-compressed',
        'application/octet-stream',
    ],
}


def validate_resume_file(uploaded_file):
    """
    Comprehensive validator for uploaded resume documents.
    Validates:
      1. Presence and non-empty size
      2. File extension via Django FileExtensionValidator(['pdf', 'doc', 'docx'])
      3. File size cap (maximum 5 MB)
      4. MIME type check
      5. Magic byte / binary signatures
    """
    if not uploaded_file:
        raise ValidationError("No file provided.")

    # 1. Django FileExtensionValidator check
    resume_extension_validator(uploaded_file)

    filename = getattr(uploaded_file, 'name', '') or ''
    file_ext = os.path.splitext(filename)[1].lower().lstrip('.')

    if not file_ext or file_ext not in ALLOWED_RESUME_EXTENSIONS:
        raise ValidationError(
            f"Unsupported file extension '.{file_ext}'. Only {', '.join(ALLOWED_RESUME_EXTENSIONS).upper()} files are permitted."
        )

    # 2. File size cap check
    file_size = getattr(uploaded_file, 'size', 0)
    if file_size == 0:
        raise ValidationError("Uploaded file is empty (0 bytes).")

    if file_size > MAX_RESUME_SIZE_BYTES:
        size_in_mb = round(file_size / (1024 * 1024), 2)
        raise ValidationError(
            f"File size exceeds the {MAX_RESUME_SIZE_MB} MB limit. Uploaded file is {size_in_mb} MB."
        )

    # 3. Content Type (MIME) check if provided
    content_type = getattr(uploaded_file, 'content_type', None)
    if content_type:
        allowed_mimes = [m.lower() for m in ALLOWED_MIME_TYPES.get(file_ext, [])]
        if content_type.lower() not in allowed_mimes and 'octet-stream' not in content_type.lower():
            raise ValidationError(
                f"Invalid MIME type '{content_type}' for .{file_ext} file."
            )

    # 4. Binary signature / magic byte inspection
    try:
        current_pos = uploaded_file.tell() if hasattr(uploaded_file, 'tell') else 0
        uploaded_file.seek(0)
        header = uploaded_file.read(8)
        uploaded_file.seek(current_pos)

        expected_signatures = FILE_SIGNATURES.get(file_ext, [])
        matches_signature = any(header.startswith(sig) for sig in expected_signatures)

        if not matches_signature:
            raise ValidationError(
                f"File content does not match legitimate .{file_ext} document structure. The file may be corrupt or disguised."
            )
    except (AttributeError, IOError):
        pass  # If file object does not support seek/read, proceed with previous checks

    return uploaded_file
