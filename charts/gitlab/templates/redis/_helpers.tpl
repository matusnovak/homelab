{{/*
Expand the name of the chart.
*/}}
{{- define "gitlab.redis.name" -}}
{{- default (printf "%s-redis" .Chart.Name) .Values.redis.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "gitlab.redis.fullname" -}}
{{- printf "%s-%s-redis" .Release.Name .Values.global.fullname.gitlab | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "gitlab.redis.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "gitlab.redis.labels" -}}
helm.sh/chart: {{ include "gitlab.redis.chart" . }}
{{ include "gitlab.redis.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "gitlab.redis.selectorLabels" -}}
app.kubernetes.io/name: {{ include "gitlab.redis.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "gitlab.redis.serviceAccountName" -}}
{{- if .Values.redis.serviceAccount.create }}
{{- default (include "gitlab.redis.fullname" .) .Values.redis.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.redis.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the role to use
*/}}
{{- define "gitlab.redis.roleName" -}}
{{- if .Values.redis.role.create }}
{{- default (include "gitlab.redis.fullname" .) .Values.redis.role.name }}
{{- else }}
{{- default "default" .Values.redis.role.name }}
{{- end }}
{{- end }}
