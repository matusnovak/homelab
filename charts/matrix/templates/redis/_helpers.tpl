{{/*
Expand the name of the chart.
*/}}
{{- define "matrix.redis.name" -}}
{{- default (printf "%s-redis" .Chart.Name) .Values.redis.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "matrix.redis.fullname" -}}
{{- printf "%s-%s-redis" .Release.Name .Values.global.fullname.matrix | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "matrix.redis.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "matrix.redis.labels" -}}
helm.sh/chart: {{ include "matrix.redis.chart" . }}
{{ include "matrix.redis.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "matrix.redis.selectorLabels" -}}
app.kubernetes.io/name: {{ include "matrix.redis.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "matrix.redis.serviceAccountName" -}}
{{- if .Values.redis.serviceAccount.create }}
{{- default (include "matrix.redis.fullname" .) .Values.redis.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.redis.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the role to use
*/}}
{{- define "matrix.redis.roleName" -}}
{{- if .Values.redis.role.create }}
{{- default (include "matrix.redis.fullname" .) .Values.redis.role.name }}
{{- else }}
{{- default "default" .Values.redis.role.name }}
{{- end }}
{{- end }}
