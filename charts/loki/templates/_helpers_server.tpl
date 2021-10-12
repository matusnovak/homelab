{{/*
Expand the name of the chart.
*/}}
{{- define "loki.server.name" -}}
{{- default (printf "%s-server" .Chart.Name) .Values.server.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "loki.server.fullname" -}}
{{- printf "%s-%s-server" .Release.Name .Values.global.fullname.loki | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "loki.server.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "loki.server.labels" -}}
helm.sh/chart: {{ include "loki.server.chart" . }}
{{ include "loki.server.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "loki.server.selectorLabels" -}}
app.kubernetes.io/name: {{ include "loki.server.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "loki.server.serviceAccountName" -}}
{{- if .Values.server.serviceAccount.create }}
{{- default (include "loki.server.fullname" .) .Values.server.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.server.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the role to use
*/}}
{{- define "loki.server.roleName" -}}
{{- if .Values.server.role.create }}
{{- default (include "loki.server.fullname" .) .Values.server.role.name }}
{{- else }}
{{- default "default" .Values.server.role.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the persistent volume to use
*/}}
{{- define "loki.server.persistentVolumeName" -}}
{{- if .Values.server.persistentVolume.create }}
{{- default (printf "%s-%s" (include "loki.server.fullname" .) "certs-pv") .Values.server.persistentVolume.name }}
{{- else }}
{{- default "default" .Values.server.persistentVolume.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the persistent volume claim to use
*/}}
{{- define "loki.server.persistentVolumeClaimName" -}}
{{- if .Values.server.persistentVolumeClaim.create }}
{{- default (printf "%s-%s" (include "loki.server.fullname" .) "certs-pvc") .Values.server.persistentVolumeClaim.name }}
{{- else }}
{{- default "default" .Values.server.persistentVolumeClaim.name }}
{{- end }}
{{- end }}
