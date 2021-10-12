{{/*
Expand the name of the chart.
*/}}
{{- define "postgres-controller.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "postgres-controller.fullname" -}}
{{- printf "%s-%s" .Release.Name .Values.global.fullname.postgresController | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified name for postgres
*/}}
{{- define "postgres.fullname" -}}
{{- printf "%s-%s" .Release.Name .Values.global.fullname.postgres | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "postgres-controller.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "postgres-controller.labels" -}}
helm.sh/chart: {{ include "postgres-controller.chart" . }}
{{ include "postgres-controller.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "postgres-controller.selectorLabels" -}}
app.kubernetes.io/name: {{ include "postgres-controller.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "postgres-controller.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "postgres-controller.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the cluster role to use
*/}}
{{- define "postgres-controller.clusterRoleName" -}}
{{- if .Values.clusterRole.create }}
{{- default (include "postgres-controller.fullname" .) .Values.clusterRole.name }}
{{- else }}
{{- default "default" .Values.clusterRole.name }}
{{- end }}
{{- end }}


{{/*
Create the name of the role to use
*/}}
{{- define "postgres-controller.roleName" -}}
{{- if .Values.role.create }}
{{- default (include "postgres-controller.fullname" .) .Values.role.name }}
{{- else }}
{{- default "default" .Values.role.name }}
{{- end }}
{{- end }}
