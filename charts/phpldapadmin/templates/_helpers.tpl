{{/*
Expand the name of the chart.
*/}}
{{- define "phpldapadmin.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "phpldapadmin.fullname" -}}
{{- printf "%s-%s" .Release.Name .Values.global.fullname.phpldapadmin | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified for traefik.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "traefik.fullname" -}}
{{- printf "%s-%s" .Release.Name .Values.global.fullname.traefik | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified for openldap.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "openldap.fullname" -}}
{{- printf "%s-%s" .Release.Name .Values.global.openldap.traefik | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "phpldapadmin.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "phpldapadmin.labels" -}}
helm.sh/chart: {{ include "phpldapadmin.chart" . }}
{{ include "phpldapadmin.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "phpldapadmin.selectorLabels" -}}
app.kubernetes.io/name: {{ include "phpldapadmin.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "phpldapadmin.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "phpldapadmin.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the role to use
*/}}
{{- define "phpldapadmin.roleName" -}}
{{- if .Values.role.create }}
{{- default (include "phpldapadmin.fullname" .) .Values.role.name }}
{{- else }}
{{- default "default" .Values.role.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the data persistent volume to use
*/}}
{{- define "phpldapadmin.persistentVolumeName.data" -}}
{{- if .Values.persistentVolume.data.create }}
{{- default (printf "%s-%s" (include "phpldapadmin.fullname" .) "data-pv") .Values.persistentVolume.data.name }}
{{- else }}
{{- default "default" .Values.persistentVolume.data.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the data persistent volume claim to use
*/}}
{{- define "phpldapadmin.persistentVolumeClaimName.data" -}}
{{- if .Values.persistentVolumeClaim.data.create }}
{{- default (printf "%s-%s" (include "phpldapadmin.fullname" .) "data-pvc") .Values.persistentVolumeClaim.data.name }}
{{- else }}
{{- default "default" .Values.persistentVolumeClaim.data.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the config persistent volume to use
*/}}
{{- define "phpldapadmin.persistentVolumeName.config" -}}
{{- if .Values.persistentVolume.config.create }}
{{- default (printf "%s-%s" (include "phpldapadmin.fullname" .) "config-pv") .Values.persistentVolume.config.name }}
{{- else }}
{{- default "default" .Values.persistentVolume.config.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the config persistent volume claim to use
*/}}
{{- define "phpldapadmin.persistentVolumeClaimName.config" -}}
{{- if .Values.persistentVolumeClaim.config.create }}
{{- default (printf "%s-%s" (include "phpldapadmin.fullname" .) "config-pvc") .Values.persistentVolumeClaim.config.name }}
{{- else }}
{{- default "default" .Values.persistentVolumeClaim.config.name }}
{{- end }}
{{- end }}
