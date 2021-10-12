{{/*
Expand the name of the chart.
*/}}
{{- define "loki.promtail.name" -}}
{{- default (printf "%s-promtail" .Chart.Name) .Values.promtail.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "loki.promtail.fullname" -}}
{{- printf "%s-%s-promtail" .Release.Name .Values.global.fullname.loki | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "loki.promtail.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "loki.promtail.labels" -}}
helm.sh/chart: {{ include "loki.promtail.chart" . }}
{{ include "loki.promtail.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "loki.promtail.selectorLabels" -}}
app.kubernetes.io/name: {{ include "loki.promtail.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "loki.promtail.serviceAccountName" -}}
{{- if .Values.promtail.serviceAccount.create }}
{{- default (include "loki.promtail.fullname" .) .Values.promtail.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.promtail.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the role to use
*/}}
{{- define "loki.promtail.roleName" -}}
{{- if .Values.promtail.role.create }}
{{- default (include "loki.promtail.fullname" .) .Values.promtail.role.name }}
{{- else }}
{{- default "default" .Values.promtail.role.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the cluster role to use
*/}}
{{- define "loki.promtail.clusterRoleName" -}}
{{- if .Values.promtail.clusterRole.create }}
{{- default (include "loki.promtail.fullname" .) .Values.promtail.clusterRole.name }}
{{- else }}
{{- default "default" .Values.promtail.clusterRole.name }}
{{- end }}
{{- end }}
