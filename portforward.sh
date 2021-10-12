docker run --rm -e REMOTE_HOST=127.0.0.1 -e REMOTE_PORT=32002 -e LOCAL_PORT=443 --net host --name homelab-https-port-forward -itd marcnuri/port-forward
docker run --rm -e REMOTE_HOST=127.0.0.1 -e REMOTE_PORT=32001 -e LOCAL_PORT=80 --net host --name homelab-http-port-forward -itd marcnuri/port-forward
