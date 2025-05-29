#!/bin/sh
set -e

# Change user/group IDs if environment variables are set
if [ -n "${HOST_UID}" ] && [ -n "${HOST_GID}" ]; then
    echo "Updating user/group IDs..."
    sudo -n deluser appuser 2>/dev/null || true
    sudo -n delgroup appgroup 2>/dev/null || true

    if getent group ${HOST_GID} >/dev/null; then
        sudo -n delgroup $(getent group ${HOST_GID} | cut -d: -f1) 2>/dev/null || true
    fi

    if getent passwd ${HOST_UID} >/dev/null; then
        sudo -n deluser $(getent passwd ${HOST_UID} | cut -d: -f1) 2>/dev/null || true
    fi

    addgroup -g ${HOST_GID} -S appgroup
    adduser -u ${HOST_UID} -S appuser -G appgroup

    chown -R appuser:appgroup /app /home/appuser
fi

exec "$@"