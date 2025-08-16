FROM kong:3.6

# Copy declarative config into image
COPY kong-config.yml /kong/declarative/kong-config.yml

ENV KONG_DATABASE=off \
    KONG_DECLARATIVE_CONFIG=/kong/declarative/kong-config.yml \
    KONG_PROXY_ACCESS_LOG=/dev/stdout \
    KONG_ADMIN_ACCESS_LOG=/dev/stdout \
    KONG_PROXY_ERROR_LOG=/dev/stderr \
    KONG_ADMIN_ERROR_LOG=/dev/stderr \
    KONG_ADMIN_LISTEN="0.0.0.0:8001, 0.0.0.0:8444 ssl"

# Expose proxy/admin ports (Render will map the ones you enable)
EXPOSE 8000 8001 8443 8444
