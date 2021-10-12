{{/*
Expand the name of the chart.
*/}}
{{- define "matrix.element.name" -}}
{{- default (printf "%s-element" .Chart.Name) .Values.element.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "matrix.element.fullname" -}}
{{- printf "%s-%s-element" .Release.Name .Values.global.fullname.matrix | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "matrix.element.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "matrix.element.labels" -}}
helm.sh/chart: {{ include "matrix.element.chart" . }}
{{ include "matrix.element.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "matrix.element.selectorLabels" -}}
app.kubernetes.io/name: {{ include "matrix.element.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "matrix.element.serviceAccountName" -}}
{{- if .Values.element.serviceAccount.create }}
{{- default (include "matrix.element.fullname" .) .Values.element.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.element.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the role to use
*/}}
{{- define "matrix.element.roleName" -}}
{{- if .Values.element.role.create }}
{{- default (include "matrix.element.fullname" .) .Values.element.role.name }}
{{- else }}
{{- default "default" .Values.element.role.name }}
{{- end }}
{{- end }}
