import time
from django.core.cache import cache
from rest_framework.throttling import AnonRateThrottle
from rest_framework.settings import api_settings


class LoadBalancerSafeThrottle(AnonRateThrottle):
    """
    Extracts the authentic client IP from HTTP_X_FORWARDED_FOR when operating
    behind reverse proxies and load balancers (e.g., Render, Nginx, AWS ALB, Cloudflare).
    Honors DRF's NUM_PROXIES setting to correctly pick the client IP.
    """
    def get_ident(self, request):
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        remote_addr = request.META.get('REMOTE_ADDR')
        num_proxies = getattr(api_settings, 'NUM_PROXIES', 1)

        if num_proxies is not None and xff:
            addrs = [addr.strip() for addr in xff.split(',')]
            if num_proxies == 0:
                return remote_addr or '127.0.0.1'
            client_index = -min(num_proxies, len(addrs))
            return addrs[client_index]
        elif xff:
            return xff.split(',')[0].strip()
        return remote_addr or '127.0.0.1'


class LoginRateThrottle(LoadBalancerSafeThrottle):
    """
    Throttles login attempts to prevent credential stuffing and brute-force attacks.
    Rate configured via settings: 'auth_login' (e.g. 5/min).
    """
    scope = 'auth_login'


class RegisterRateThrottle(LoadBalancerSafeThrottle):
    """
    Throttles registration attempts and registration OTP requests to prevent spam signups.
    Rate configured via settings: 'auth_register' (e.g. 5/min).
    """
    scope = 'auth_register'


class PasswordResetRateThrottle(LoadBalancerSafeThrottle):
    """
    Throttles password reset requests and verification to prevent email bombing and enumeration.
    Rate configured via settings: 'auth_password_reset' (e.g. 3/min).
    """
    scope = 'auth_password_reset'


class OTPRateThrottle(LoadBalancerSafeThrottle):
    """
    Throttles OTP generation and verification to prevent brute-forcing 6-digit verification codes.
    Rate configured via settings: 'auth_otp' (e.g. 5/min).
    """
    scope = 'auth_otp'


# ─────────────────────────────────────────────────────────
# ACCOUNT LOCKOUT DEFENSE (Concealed Brute-Force Shield)
# ─────────────────────────────────────────────────────────

LOCKOUT_THRESHOLD = 5          # 5 consecutive failed attempts
LOCKOUT_DURATION = 900         # 15 minutes lockout (900 seconds)
FAILED_ATTEMPT_WINDOW = 900    # 15 minutes failure tracking window


def get_client_ip(request):
    """Utility to retrieve authentic client IP honoring reverse proxies and load balancers."""
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    num_proxies = getattr(api_settings, 'NUM_PROXIES', 1)
    if num_proxies is not None and xff:
        addrs = [a.strip() for a in xff.split(',')]
        if num_proxies == 0:
            return request.META.get('REMOTE_ADDR') or '127.0.0.1'
        return addrs[-min(num_proxies, len(addrs))]
    elif xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR') or '127.0.0.1'


def is_account_locked(identifier, client_ip):
    """
    Checks if an account identifier or client IP is currently locked out.
    Returns: (is_locked: bool, remaining_seconds: int)
    """
    clean_id = str(identifier).lower().strip()
    ident_key = f"lockout:user:{clean_id}"
    ip_key = f"lockout:ip:{client_ip}"

    user_lock_until = cache.get(ident_key)
    ip_lock_until = cache.get(ip_key)
    now = time.time()

    if user_lock_until and user_lock_until > now:
        return True, int(user_lock_until - now)
    if ip_lock_until and ip_lock_until > now:
        return True, int(ip_lock_until - now)

    return False, 0


def record_failed_attempt(identifier, client_ip):
    """
    Records a failed login attempt for the user identifier and client IP.
    Enforces lockout if the consecutive threshold is reached.
    Returns: (is_locked: bool, attempts_count: int, remaining_seconds: int)
    """
    clean_id = str(identifier).lower().strip()
    user_fail_key = f"failed_attempts:user:{clean_id}"
    ip_fail_key = f"failed_attempts:ip:{client_ip}"

    user_attempts = (cache.get(user_fail_key) or 0) + 1
    ip_attempts = (cache.get(ip_fail_key) or 0) + 1

    cache.set(user_fail_key, user_attempts, timeout=FAILED_ATTEMPT_WINDOW)
    cache.set(ip_fail_key, ip_attempts, timeout=FAILED_ATTEMPT_WINDOW)

    max_attempts = max(user_attempts, ip_attempts)

    if max_attempts >= LOCKOUT_THRESHOLD:
        lock_until = time.time() + LOCKOUT_DURATION
        if clean_id:
            cache.set(f"lockout:user:{clean_id}", lock_until, timeout=LOCKOUT_DURATION)
        cache.set(f"lockout:ip:{client_ip}", lock_until, timeout=LOCKOUT_DURATION)
        return True, max_attempts, LOCKOUT_DURATION

    return False, max_attempts, 0


def clear_failed_attempts(identifier, client_ip):
    """Clears failed attempt counters and lockout flags upon successful authentication."""
    clean_id = str(identifier).lower().strip()
    if clean_id:
        cache.delete(f"failed_attempts:user:{clean_id}")
        cache.delete(f"lockout:user:{clean_id}")
    cache.delete(f"failed_attempts:ip:{client_ip}")
    cache.delete(f"lockout:ip:{client_ip}")
