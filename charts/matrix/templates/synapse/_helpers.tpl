{{/*
Expand the name of the chart.
*/}}
{{- define "matrix.synapse.name" -}}
{{- default (printf "%s-synapse" .Chart.Name) .Values.synapse.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "matrix.synapse.fullname" -}}
{{- printf "%s-%s-synapse" .Release.Name .Values.global.fullname.matrix | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "matrix.synapse.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "matrix.synapse.labels" -}}
helm.sh/chart: {{ include "matrix.synapse.chart" . }}
{{ include "matrix.synapse.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "matrix.synapse.selectorLabels" -}}
app.kubernetes.io/name: {{ include "matrix.synapse.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "matrix.synapse.serviceAccountName" -}}
{{- if .Values.synapse.serviceAccount.create }}
{{- default (include "matrix.synapse.fullname" .) .Values.synapse.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.synapse.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the role to use
*/}}
{{- define "matrix.synapse.roleName" -}}
{{- if .Values.synapse.role.create }}
{{- default (include "matrix.synapse.fullname" .) .Values.synapse.role.name }}
{{- else }}
{{- default "default" .Values.synapse.role.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the persistent volume to use
*/}}
{{- define "matrix.synapse.persistentVolumeName" -}}
{{- if .Values.synapse.persistentVolume.create }}
{{- default (printf "%s-%s" (include "matrix.synapse.fullname" .) "certs-pv") .Values.synapse.persistentVolume.name }}
{{- else }}
{{- default "default" .Values.synapse.persistentVolume.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the persistent volume claim to use
*/}}
{{- define "matrix.synapse.persistentVolumeClaimName" -}}
{{- if .Values.synapse.persistentVolumeClaim.create }}
{{- default (printf "%s-%s" (include "matrix.synapse.fullname" .) "certs-pvc") .Values.synapse.persistentVolumeClaim.name }}
{{- else }}
{{- default "default" .Values.synapse.persistentVolumeClaim.name }}
{{- end }}
{{- end }}
