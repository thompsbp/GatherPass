# This Dockerfile creates a custom Caddy image with the rate-limit module.

# Use the official Caddy builder image which contains the 'xcaddy' tool.
FROM caddy:2-builder AS builder

# Use xcaddy to compile a new Caddy binary that includes the rate-limit plugin.
RUN xcaddy build \
    --with github.com/mholt/caddy-ratelimit

# Start a new, clean stage using the lightweight alpine image.
FROM caddy:2-alpine

# Copy the custom-built Caddy binary from the 'builder' stage into this
# final image, replacing the standard one.
COPY --from=builder /usr/bin/caddy /usr/bin/caddy
