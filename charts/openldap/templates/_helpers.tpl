{{/*
Expand the name of the chart.
*/}}
{{- define "openldap.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "openldap.fullname" -}}
{{- printf "%s-%s" .Release.Name .Values.global.fullname.openldap | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "openldap.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "openldap.labels" -}}
helm.sh/chart: {{ include "openldap.chart" . }}
{{ include "openldap.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "openldap.selectorLabels" -}}
app.kubernetes.io/name: {{ include "openldap.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "openldap.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "openldap.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the role to use
*/}}
{{- define "openldap.roleName" -}}
{{- if .Values.role.create }}
{{- default (include "openldap.fullname" .) .Values.role.name }}
{{- else }}
{{- default "default" .Values.role.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the data persistent volume to use
*/}}
{{- define "openldap.persistentVolumeName.data" -}}
{{- if .Values.persistentVolume.data.create }}
{{- default (printf "%s-%s" (include "openldap.fullname" .) "data-pv") .Values.persistentVolume.data.name }}
{{- else }}
{{- default "default" .Values.persistentVolume.data.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the data persistent volume claim to use
*/}}
{{- define "openldap.persistentVolumeClaimName.data" -}}
{{- if .Values.persistentVolumeClaim.data.create }}
{{- default (printf "%s-%s" (include "openldap.fullname" .) "data-pvc") .Values.persistentVolumeClaim.data.name }}
{{- else }}
{{- default "default" .Values.persistentVolumeClaim.data.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the config persistent volume to use
*/}}
{{- define "openldap.persistentVolumeName.config" -}}
{{- if .Values.persistentVolume.config.create }}
{{- default (printf "%s-%s" (include "openldap.fullname" .) "config-pv") .Values.persistentVolume.config.name }}
{{- else }}
{{- default "default" .Values.persistentVolume.config.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the config persistent volume claim to use
*/}}
{{- define "openldap.persistentVolumeClaimName.config" -}}
{{- if .Values.persistentVolumeClaim.config.create }}
{{- default (printf "%s-%s" (include "openldap.fullname" .) "config-pvc") .Values.persistentVolumeClaim.config.name }}
{{- else }}
{{- default "default" .Values.persistentVolumeClaim.config.name }}
{{- end }}
{{- end }}
