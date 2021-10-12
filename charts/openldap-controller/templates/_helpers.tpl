{{/*
Expand the name of the chart.
*/}}
{{- define "openldap-controller.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "openldap-controller.fullname" -}}
{{- printf "%s-%s" .Release.Name .Values.global.fullname.openldapController | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified name for openldap
*/}}
{{- define "openldap.fullname" -}}
{{- printf "%s-%s" .Release.Name .Values.global.fullname.openldap | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "openldap-controller.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "openldap-controller.labels" -}}
helm.sh/chart: {{ include "openldap-controller.chart" . }}
{{ include "openldap-controller.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "openldap-controller.selectorLabels" -}}
app.kubernetes.io/name: {{ include "openldap-controller.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "openldap-controller.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "openldap-controller.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the cluster role to use
*/}}
{{- define "openldap-controller.clusterRoleName" -}}
{{- if .Values.clusterRole.create }}
{{- default (include "openldap-controller.fullname" .) .Values.clusterRole.name }}
{{- else }}
{{- default "default" .Values.clusterRole.name }}
{{- end }}
{{- end }}


{{/*
Create the name of the role to use
*/}}
{{- define "openldap-controller.roleName" -}}
{{- if .Values.role.create }}
{{- default (include "openldap-controller.fullname" .) .Values.role.name }}
{{- else }}
{{- default "default" .Values.role.name }}
{{- end }}
{{- end }}
