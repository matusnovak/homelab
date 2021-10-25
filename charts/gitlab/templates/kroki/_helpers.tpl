{{/*
Expand the name of the chart.
*/}}
{{- define "gitlab.kroki.name" -}}
{{- default (printf "%s-kroki" .Chart.Name) .Values.kroki.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "gitlab.kroki.fullname" -}}
{{- printf "%s-%s-kroki" .Release.Name .Values.global.fullname.gitlab | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "gitlab.kroki.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "gitlab.kroki.labels" -}}
helm.sh/chart: {{ include "gitlab.kroki.chart" . }}
{{ include "gitlab.kroki.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "gitlab.kroki.selectorLabels" -}}
app.kubernetes.io/name: {{ include "gitlab.kroki.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "gitlab.kroki.serviceAccountName" -}}
{{- if .Values.kroki.serviceAccount.create }}
{{- default (include "gitlab.kroki.fullname" .) .Values.kroki.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.kroki.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the role to use
*/}}
{{- define "gitlab.kroki.roleName" -}}
{{- if .Values.kroki.role.create }}
{{- default (include "gitlab.kroki.fullname" .) .Values.kroki.role.name }}
{{- else }}
{{- default "default" .Values.kroki.role.name }}
{{- end }}
{{- end }}
