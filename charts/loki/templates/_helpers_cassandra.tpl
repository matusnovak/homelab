{{/*
Expand the name of the chart.
*/}}
{{- define "loki.cassandra.name" -}}
{{- default (printf "%s-cassandra" .Chart.Name) .Values.cassandra.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "loki.cassandra.fullname" -}}
{{- printf "%s-%s-cassandra" .Release.Name .Values.global.fullname.loki | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "loki.cassandra.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "loki.cassandra.labels" -}}
helm.sh/chart: {{ include "loki.cassandra.chart" . }}
{{ include "loki.cassandra.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "loki.cassandra.selectorLabels" -}}
app.kubernetes.io/name: {{ include "loki.cassandra.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "loki.cassandra.serviceAccountName" -}}
{{- if .Values.cassandra.serviceAccount.create }}
{{- default (include "loki.cassandra.fullname" .) .Values.cassandra.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.cassandra.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the role to use
*/}}
{{- define "loki.cassandra.roleName" -}}
{{- if .Values.cassandra.role.create }}
{{- default (include "loki.cassandra.fullname" .) .Values.cassandra.role.name }}
{{- else }}
{{- default "default" .Values.cassandra.role.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the persistent volume to use
*/}}
{{- define "loki.cassandra.persistentVolumeName" -}}
{{- if .Values.cassandra.persistentVolume.create }}
{{- default (printf "%s-%s" (include "loki.cassandra.fullname" .) "certs-pv") .Values.cassandra.persistentVolume.name }}
{{- else }}
{{- default "default" .Values.cassandra.persistentVolume.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the persistent volume claim to use
*/}}
{{- define "loki.cassandra.persistentVolumeClaimName" -}}
{{- if .Values.cassandra.persistentVolumeClaim.create }}
{{- default (printf "%s-%s" (include "loki.cassandra.fullname" .) "certs-pvc") .Values.cassandra.persistentVolumeClaim.name }}
{{- else }}
{{- default "default" .Values.cassandra.persistentVolumeClaim.name }}
{{- end }}
{{- end }}
