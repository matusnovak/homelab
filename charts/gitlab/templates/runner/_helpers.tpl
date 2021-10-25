{{/*
Expand the name of the chart.
*/}}
{{- define "gitlab.runner.name" -}}
{{- default (printf "%s-runner" .Chart.Name) .Values.runner.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "gitlab.runner.fullname" -}}
{{- printf "%s-%s-runner" .Release.Name .Values.global.fullname.gitlab | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "gitlab.runner.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "gitlab.runner.labels" -}}
helm.sh/chart: {{ include "gitlab.runner.chart" . }}
{{ include "gitlab.runner.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "gitlab.runner.selectorLabels" -}}
app.kubernetes.io/name: {{ include "gitlab.runner.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "gitlab.runner.serviceAccountName" -}}
{{- if .Values.runner.serviceAccount.create }}
{{- default (include "gitlab.runner.fullname" .) .Values.runner.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.runner.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the role to use
*/}}
{{- define "gitlab.runner.roleName" -}}
{{- if .Values.runner.role.create }}
{{- default (include "gitlab.runner.fullname" .) .Values.runner.role.name }}
{{- else }}
{{- default "default" .Values.runner.role.name }}
{{- end }}
{{- end }}
