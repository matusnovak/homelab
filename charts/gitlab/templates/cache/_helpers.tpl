{{/*
Expand the name of the chart.
*/}}
{{- define "gitlab.cache.name" -}}
{{- default (printf "%s-cache" .Chart.Name) .Values.cache.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "gitlab.cache.fullname" -}}
{{- printf "%s-%s-cache" .Release.Name .Values.global.fullname.gitlab | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "gitlab.cache.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "gitlab.cache.labels" -}}
helm.sh/chart: {{ include "gitlab.cache.chart" . }}
{{ include "gitlab.cache.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "gitlab.cache.selectorLabels" -}}
app.kubernetes.io/name: {{ include "gitlab.cache.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "gitlab.cache.serviceAccountName" -}}
{{- if .Values.cache.serviceAccount.create }}
{{- default (include "gitlab.cache.fullname" .) .Values.cache.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.cache.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the role to use
*/}}
{{- define "gitlab.cache.roleName" -}}
{{- if .Values.cache.role.create }}
{{- default (include "gitlab.cache.fullname" .) .Values.cache.role.name }}
{{- else }}
{{- default "default" .Values.cache.role.name }}
{{- end }}
{{- end }}
