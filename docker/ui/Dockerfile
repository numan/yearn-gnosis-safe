FROM --platform=linux/x86_64 nginx:latest

ARG ENVIRONMENT_NAME

COPY builds/build_${ENVIRONMENT_NAME} /usr/share/nginx/html

