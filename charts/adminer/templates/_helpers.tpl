{{/*
Expand the name of the chart.
*/}}
{{- define "adminer.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "adminer.fullname" -}}
{{- printf "%s-%s" .Release.Name .Values.global.fullname.adminer | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified for traefik.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "traefik.fullname" -}}
{{- printf "%s-%s" .Release.Name .Values.global.fullname.traefik | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified for postgres.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "postgres.fullname" -}}
{{- printf "%s-%s" .Release.Name .Values.global.fullname.postgres | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "adminer.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "adminer.labels" -}}
helm.sh/chart: {{ include "adminer.chart" . }}
{{ include "adminer.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "adminer.selectorLabels" -}}
app.kubernetes.io/name: {{ include "adminer.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "adminer.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "adminer.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the role to use
*/}}
{{- define "adminer.roleName" -}}
{{- if .Values.role.create }}
{{- default (include "adminer.fullname" .) .Values.role.name }}
{{- else }}
{{- default "default" .Values.role.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the data persistent volume to use
*/}}
{{- define "adminer.persistentVolumeName.data" -}}
{{- if .Values.persistentVolume.data.create }}
{{- default (printf "%s-%s" (include "adminer.fullname" .) "data-pv") .Values.persistentVolume.data.name }}
{{- else }}
{{- default "default" .Values.persistentVolume.data.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the data persistent volume claim to use
*/}}
{{- define "adminer.persistentVolumeClaimName.data" -}}
{{- if .Values.persistentVolumeClaim.data.create }}
{{- default (printf "%s-%s" (include "adminer.fullname" .) "data-pvc") .Values.persistentVolumeClaim.data.name }}
{{- else }}
{{- default "default" .Values.persistentVolumeClaim.data.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the config persistent volume to use
*/}}
{{- define "adminer.persistentVolumeName.config" -}}
{{- if .Values.persistentVolume.config.create }}
{{- default (printf "%s-%s" (include "adminer.fullname" .) "config-pv") .Values.persistentVolume.config.name }}
{{- else }}
{{- default "default" .Values.persistentVolume.config.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the config persistent volume claim to use
*/}}
{{- define "adminer.persistentVolumeClaimName.config" -}}
{{- if .Values.persistentVolumeClaim.config.create }}
{{- default (printf "%s-%s" (include "adminer.fullname" .) "config-pvc") .Values.persistentVolumeClaim.config.name }}
{{- else }}
{{- default "default" .Values.persistentVolumeClaim.config.name }}
{{- end }}
{{- end }}
