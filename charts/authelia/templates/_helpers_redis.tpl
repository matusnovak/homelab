{{/*
Expand the name of the chart.
*/}}
{{- define "authelia.redis.name" -}}
{{- default (printf "%s-redis" .Chart.Name) .Values.redis.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "authelia.redis.fullname" -}}
{{- printf "%s-%s-redis" .Release.Name .Values.global.fullname.authelia | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "authelia.redis.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "authelia.redis.labels" -}}
helm.sh/chart: {{ include "authelia.redis.chart" . }}
{{ include "authelia.redis.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "authelia.redis.selectorLabels" -}}
app.kubernetes.io/name: {{ include "authelia.redis.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "authelia.redis.serviceAccountName" -}}
{{- if .Values.redis.serviceAccount.create }}
{{- default (include "authelia.redis.fullname" .) .Values.redis.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.redis.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the role to use
*/}}
{{- define "authelia.redis.roleName" -}}
{{- if .Values.redis.role.create }}
{{- default (include "authelia.redis.fullname" .) .Values.redis.role.name }}
{{- else }}
{{- default "default" .Values.redis.role.name }}
{{- end }}
{{- end }}
