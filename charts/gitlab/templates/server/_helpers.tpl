{{/*
Expand the name of the chart.
*/}}
{{- define "gitlab.server.name" -}}
{{- default (printf "%s-server" .Chart.Name) .Values.server.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "gitlab.server.fullname" -}}
{{- printf "%s-%s-server" .Release.Name .Values.global.fullname.gitlab | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "gitlab.server.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "gitlab.server.labels" -}}
helm.sh/chart: {{ include "gitlab.server.chart" . }}
{{ include "gitlab.server.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "gitlab.server.selectorLabels" -}}
app.kubernetes.io/name: {{ include "gitlab.server.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "gitlab.server.serviceAccountName" -}}
{{- if .Values.server.serviceAccount.create }}
{{- default (include "gitlab.server.fullname" .) .Values.server.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.server.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the role to use
*/}}
{{- define "gitlab.server.roleName" -}}
{{- if .Values.server.role.create }}
{{- default (include "gitlab.server.fullname" .) .Values.server.role.name }}
{{- else }}
{{- default "default" .Values.server.role.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the persistent volume to use
*/}}
{{- define "gitlab.server.persistentVolumeName.logs" -}}
{{- if .Values.server.persistentVolume.logs.create }}
{{- default (printf "%s-%s" (include "gitlab.server.fullname" .) "logs-pv") .Values.server.persistentVolume.logs.name }}
{{- else }}
{{- default "default" .Values.server.persistentVolume.logs.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the persistent volume claim to use
*/}}
{{- define "gitlab.server.persistentVolumeClaimName.logs" -}}
{{- if .Values.server.persistentVolumeClaim.logs.create }}
{{- default (printf "%s-%s" (include "gitlab.server.fullname" .) "logs-pvc") .Values.server.persistentVolumeClaim.logs.name }}
{{- else }}
{{- default "default" .Values.server.persistentVolumeClaim.logs.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the persistent volume to use
*/}}
{{- define "gitlab.server.persistentVolumeName.config" -}}
{{- if .Values.server.persistentVolume.config.create }}
{{- default (printf "%s-%s" (include "gitlab.server.fullname" .) "config-pv") .Values.server.persistentVolume.config.name }}
{{- else }}
{{- default "default" .Values.server.persistentVolume.config.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the persistent volume claim to use
*/}}
{{- define "gitlab.server.persistentVolumeClaimName.config" -}}
{{- if .Values.server.persistentVolumeClaim.config.create }}
{{- default (printf "%s-%s" (include "gitlab.server.fullname" .) "config-pvc") .Values.server.persistentVolumeClaim.config.name }}
{{- else }}
{{- default "default" .Values.server.persistentVolumeClaim.config.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the persistent volume to use
*/}}
{{- define "gitlab.server.persistentVolumeName.data" -}}
{{- if .Values.server.persistentVolume.data.create }}
{{- default (printf "%s-%s" (include "gitlab.server.fullname" .) "data-pv") .Values.server.persistentVolume.data.name }}
{{- else }}
{{- default "default" .Values.server.persistentVolume.data.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the persistent volume claim to use
*/}}
{{- define "gitlab.server.persistentVolumeClaimName.data" -}}
{{- if .Values.server.persistentVolumeClaim.data.create }}
{{- default (printf "%s-%s" (include "gitlab.server.fullname" .) "data-pvc") .Values.server.persistentVolumeClaim.data.name }}
{{- else }}
{{- default "default" .Values.server.persistentVolumeClaim.data.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the persistent volume to use
*/}}
{{- define "gitlab.server.persistentVolumeName.git" -}}
{{- if .Values.server.persistentVolume.git.create }}
{{- default (printf "%s-%s" (include "gitlab.server.fullname" .) "git-pv") .Values.server.persistentVolume.git.name }}
{{- else }}
{{- default "default" .Values.server.persistentVolume.git.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the persistent volume claim to use
*/}}
{{- define "gitlab.server.persistentVolumeClaimName.git" -}}
{{- if .Values.server.persistentVolumeClaim.git.create }}
{{- default (printf "%s-%s" (include "gitlab.server.fullname" .) "git-pvc") .Values.server.persistentVolumeClaim.git.name }}
{{- else }}
{{- default "default" .Values.server.persistentVolumeClaim.git.name }}
{{- end }}
{{- end }}
