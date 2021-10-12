{{/*
Expand the name of the chart.
*/}}
{{- define "matrix.nginx.name" -}}
{{- default (printf "%s-nginx" .Chart.Name) .Values.nginx.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "matrix.nginx.fullname" -}}
{{- printf "%s-%s-nginx" .Release.Name .Values.global.fullname.matrix | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "matrix.nginx.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "matrix.nginx.labels" -}}
helm.sh/chart: {{ include "matrix.nginx.chart" . }}
{{ include "matrix.nginx.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "matrix.nginx.selectorLabels" -}}
app.kubernetes.io/name: {{ include "matrix.nginx.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "matrix.nginx.serviceAccountName" -}}
{{- if .Values.nginx.serviceAccount.create }}
{{- default (include "matrix.nginx.fullname" .) .Values.nginx.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.nginx.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the role to use
*/}}
{{- define "matrix.nginx.roleName" -}}
{{- if .Values.nginx.role.create }}
{{- default (include "matrix.nginx.fullname" .) .Values.nginx.role.name }}
{{- else }}
{{- default "default" .Values.nginx.role.name }}
{{- end }}
{{- end }}
