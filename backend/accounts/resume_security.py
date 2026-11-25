import os
import mimetypes
from django.conf import settings
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired

RESUME_SIGNER_SALT = 'jobcrest.resume.security.v1'
DEFAULT_RESUME_EXPIRY_SECONDS = 3600  # 1 hour expiration


def generate_signed_resume_url(file_field_or_name, request=None, expires_in=DEFAULT_RESUME_EXPIRY_SECONDS):
    """
    Generates a cryptographically signed, expiring URL for resume downloads.
    """
    if not file_field_or_name:
        return None

    # Get clean relative storage path
    file_path = str(file_field_or_name).strip()
    if not file_path:
        return None

    signer = TimestampSigner(salt=RESUME_SIGNER_SALT)
    token = signer.sign(file_path)

    relative_url = f"/api/jobseeker/resume/download/?token={token}"
    if request:
        try:
            return request.build_absolute_uri(relative_url)
        except Exception:
            return relative_url
    return relative_url


def verify_signed_resume_token(token, max_age=DEFAULT_RESUME_EXPIRY_SECONDS):
    """
    Verifies that the signed token is authentic and unexpired.
    Returns the target file relative path.
    Raises SignatureExpired or BadSignature on failure.
    """
    if not token:
        raise BadSignature("No token provided.")
    signer = TimestampSigner(salt=RESUME_SIGNER_SALT)
    return signer.unsign(token, max_age=max_age)
