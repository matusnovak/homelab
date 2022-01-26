```
/var/lib/rancher/k3s/server/manifests/traefik-config.yaml
```

```yml
apiVersion: helm.cattle.io/v1
kind: HelmChartConfig
metadata:
  name: traefik
  namespace: kube-system
spec:
  valuesContent: |-
    metrics:
      prometheus:
        enabled: false
    persistence:
      enabled: false
    ports:
      web:
        redirectTo: websecure
      websecure:
        tls:
          enabled: true
          certResolver: 'letsencrypt'
          domains:
            - main: 'example.com'
              sans:
                - '*.example.com'
    additionalArguments:
      - '--certificatesresolvers.letsencrypt.acme.dnschallenge=true'
      - '--certificatesresolvers.letsencrypt.acme.dnschallenge.provider=route53'
      - '--certificatesresolvers.letsencrypt.acme.email=example@example.com'
      - '--certificatesresolvers.letsencrypt.acme.caserver=https://acme-v02.api.letsencrypt.org/directory'
      - '--certificatesresolvers.letsencrypt.acme.storage=/data/acme.json'
    env:
      - name: AWS_ACCESS_KEY_ID
        value: '...'
      - name: AWS_SECRET_ACCESS_KEY
        value: '...'
      - name: AWS_REGION
        value: 'eu-west-1'
      - name: AWS_HOSTED_ZONE_ID
        value: '...'
```

```yml
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: kube-system-traefik-data-pv
spec:
  storageClassName: default
  capacity:
    storage: 128Mi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  hostPath:
    path: /homelab/traefik/data
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: traefik-data-pvc
  namespace: kube-system
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 128Mi
  storageClassName: default
  volumeName: kube-system-traefik-data-pv
```
