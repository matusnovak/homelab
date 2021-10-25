{{/*
Expand the name of the chart.
*/}}
{{- define "gitlab.minio.name" -}}
{{- default (printf "%s-minio" .Chart.Name) .Values.minio.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "gitlab.minio.fullname" -}}
{{- printf "%s-%s-minio" .Release.Name .Values.global.fullname.gitlab | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "gitlab.minio.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "gitlab.minio.labels" -}}
helm.sh/chart: {{ include "gitlab.minio.chart" . }}
{{ include "gitlab.minio.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "gitlab.minio.selectorLabels" -}}
app.kubernetes.io/name: {{ include "gitlab.minio.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "gitlab.minio.serviceAccountName" -}}
{{- if .Values.minio.serviceAccount.create }}
{{- default (include "gitlab.minio.fullname" .) .Values.minio.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.minio.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the role to use
*/}}
{{- define "gitlab.minio.roleName" -}}
{{- if .Values.minio.role.create }}
{{- default (include "gitlab.minio.fullname" .) .Values.minio.role.name }}
{{- else }}
{{- default "default" .Values.minio.role.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the persistent volume to use
*/}}
{{- define "gitlab.minio.persistentVolumeName" -}}
{{- if .Values.minio.persistentVolume.create }}
{{- default (printf "%s-%s" (include "gitlab.minio.fullname" .) "pv") .Values.minio.persistentVolume.name }}
{{- else }}
{{- default "default" .Values.minio.persistentVolume.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the persistent volume claim to use
*/}}
{{- define "gitlab.minio.persistentVolumeClaimName" -}}
{{- if .Values.minio.persistentVolumeClaim.create }}
{{- default (printf "%s-%s" (include "gitlab.minio.fullname" .) "pvc") .Values.minio.persistentVolumeClaim.name }}
{{- else }}
{{- default "default" .Values.minio.persistentVolumeClaim.name }}
{{- end }}
{{- end }}
