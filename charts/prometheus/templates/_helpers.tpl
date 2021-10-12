{{/*
Expand the name of the chart.
*/}}
{{- define "prometheus.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "prometheus.fullname" -}}
{{- printf "%s-%s" .Release.Name .Values.global.fullname.prometheus | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified for traefik.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "traefik.fullname" -}}
{{- printf "%s-%s" .Release.Name .Values.global.fullname.traefik | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "prometheus.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "prometheus.labels" -}}
helm.sh/chart: {{ include "prometheus.chart" . }}
{{ include "prometheus.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "prometheus.selectorLabels" -}}
app.kubernetes.io/name: {{ include "prometheus.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "prometheus.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "prometheus.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the role to use
*/}}
{{- define "prometheus.roleName" -}}
{{- if .Values.role.create }}
{{- default (include "prometheus.fullname" .) .Values.role.name }}
{{- else }}
{{- default "default" .Values.role.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the cluster role to use
*/}}
{{- define "prometheus.clusterRoleName" -}}
{{- if .Values.clusterRole.create }}
{{- default (include "prometheus.fullname" .) .Values.clusterRole.name }}
{{- else }}
{{- default "default" .Values.clusterRole.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the persistent volume to use
*/}}
{{- define "prometheus.persistentVolumeName" -}}
{{- if .Values.persistentVolume.create }}
{{- default (printf "%s-%s" (include "prometheus.fullname" .) "certs-pv") .Values.persistentVolume.name }}
{{- else }}
{{- default "default" .Values.persistentVolume.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the persistent volume claim to use
*/}}
{{- define "prometheus.persistentVolumeClaimName" -}}
{{- if .Values.persistentVolumeClaim.create }}
{{- default (printf "%s-%s" (include "prometheus.fullname" .) "certs-pvc") .Values.persistentVolumeClaim.name }}
{{- else }}
{{- default "default" .Values.persistentVolumeClaim.name }}
{{- end }}
{{- end }}
