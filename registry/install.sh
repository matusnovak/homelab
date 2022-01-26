#!/usr/bin/env bash

set -e

HOSTNAME=$(cat /etc/hostname).lan
USER=registry
PASSWORD=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 32 ; echo '')

docker run --entrypoint htpasswd httpd:2 -Bbn $USER $PASSWORD > htpasswd

if [ ! -f "registry.crt" ]; then
  openssl req \
    -newkey rsa:4096 -nodes -sha256 -keyout registry.key \
    -subj "/C=US/ST=/L=/O=/CN=$HOSTNAME" \
    -addext "subjectAltName = DNS:$HOSTNAME" \
    -x509 -days 365 -out registry.crt
fi

sudo cp registry.crt /usr/local/share/ca-certificates/$HOSTNAME.crt
sudo update-ca-certificates

sudo service docker restart

docker-compose down || true
docker-compose up -d

echo "User: $USER"
echo "Password: $PASSWORD"

echo $PASSWORD | docker login --username $USER $HOSTNAME:5443 --password-stdin

# Add to: /etc/rancher/k3s/registries.yaml
# 
# configs:
#  "homelab.local:5443":
#    auth:
#      username: registry
#      password: ...
#    tls:
#      cert_file: /home/ubuntu/homelab/registry/registry.crt
#      key_file: /home/ubuntu/homelab/registry/registry.key
