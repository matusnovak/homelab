{{/*
Expand the name of the chart.
*/}}
{{- define "traefik.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "traefik.fullname" -}}
{{- printf "%s-%s" .Release.Name .Values.global.fullname.traefik | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified name for authelia
*/}}
{{- define "authelia.fullname" -}}
{{- printf "%s-%s-server" .Release.Name .Values.global.fullname.authelia | trunc 63 | trimSuffix "-" }}
{{- end }}


{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "traefik.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "traefik.labels" -}}
helm.sh/chart: {{ include "traefik.chart" . }}
{{ include "traefik.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "traefik.selectorLabels" -}}
app.kubernetes.io/name: {{ include "traefik.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "traefik.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "traefik.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the role to use
*/}}
{{- define "traefik.roleName" -}}
{{- if .Values.role.create }}
{{- default (include "traefik.fullname" .) .Values.role.name }}
{{- else }}
{{- default "default" .Values.role.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the cluster role to use
*/}}
{{- define "traefik.clusterRoleName" -}}
{{- if .Values.clusterRole.create }}
{{- default (include "traefik.fullname" .) .Values.clusterRole.name }}
{{- else }}
{{- default "default" .Values.clusterRole.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the persistent volume to use
*/}}
{{- define "traefik.persistentVolumeName" -}}
{{- if .Values.persistentVolume.create }}
{{- default (printf "%s-%s" (include "traefik.fullname" .) "certs-pv") .Values.persistentVolume.name }}
{{- else }}
{{- default "default" .Values.persistentVolume.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the persistent volume claim to use
*/}}
{{- define "traefik.persistentVolumeClaimName" -}}
{{- if .Values.persistentVolumeClaim.create }}
{{- default (printf "%s-%s" (include "traefik.fullname" .) "certs-pvc") .Values.persistentVolumeClaim.name }}
{{- else }}
{{- default "default" .Values.persistentVolumeClaim.name }}
{{- end }}
{{- end }}
