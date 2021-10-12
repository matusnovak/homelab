{{/*
Expand the name of the chart.
*/}}
{{- define "authelia.server.name" -}}
{{- default (printf "%s-server" .Chart.Name) .Values.server.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "authelia.server.fullname" -}}
{{- printf "%s-%s-server" .Release.Name .Values.global.fullname.authelia | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "authelia.server.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "authelia.server.labels" -}}
helm.sh/chart: {{ include "authelia.server.chart" . }}
{{ include "authelia.server.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "authelia.server.selectorLabels" -}}
app.kubernetes.io/name: {{ include "authelia.server.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "authelia.server.serviceAccountName" -}}
{{- if .Values.server.serviceAccount.create }}
{{- default (include "authelia.server.fullname" .) .Values.server.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.server.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the role to use
*/}}
{{- define "authelia.server.roleName" -}}
{{- if .Values.server.role.create }}
{{- default (include "authelia.server.fullname" .) .Values.server.role.name }}
{{- else }}
{{- default "default" .Values.server.role.name }}
{{- end }}
{{- end }}
