{{/*
Expand the name of the chart.
*/}}
{{- define "nextcloud.server.name" -}}
{{- default (printf "%s-server" .Chart.Name) .Values.server.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "nextcloud.server.fullname" -}}
{{- printf "%s-%s-server" .Release.Name .Values.global.fullname.nextcloud | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "nextcloud.server.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "nextcloud.server.labels" -}}
helm.sh/chart: {{ include "nextcloud.server.chart" . }}
{{ include "nextcloud.server.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "nextcloud.server.selectorLabels" -}}
app.kubernetes.io/name: {{ include "nextcloud.server.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "nextcloud.server.serviceAccountName" -}}
{{- if .Values.server.serviceAccount.create }}
{{- default (include "nextcloud.server.fullname" .) .Values.server.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.server.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the role to use
*/}}
{{- define "nextcloud.server.roleName" -}}
{{- if .Values.server.role.create }}
{{- default (include "nextcloud.server.fullname" .) .Values.server.role.name }}
{{- else }}
{{- default "default" .Values.server.role.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the persistent volume to use
*/}}
{{- define "nextcloud.server.persistentVolumeName.html" -}}
{{- if .Values.server.persistentVolume.html.create }}
{{- default (printf "%s-%s" (include "nextcloud.server.fullname" .) "html-pv") .Values.server.persistentVolume.html.name }}
{{- else }}
{{- default "default" .Values.server.persistentVolume.html.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the persistent volume claim to use
*/}}
{{- define "nextcloud.server.persistentVolumeClaimName.html" -}}
{{- if .Values.server.persistentVolumeClaim.html.create }}
{{- default (printf "%s-%s" (include "nextcloud.server.fullname" .) "html-pvc") .Values.server.persistentVolumeClaim.html.name }}
{{- else }}
{{- default "default" .Values.server.persistentVolumeClaim.html.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the persistent volume to use
*/}}
{{- define "nextcloud.server.persistentVolumeName.config" -}}
{{- if .Values.server.persistentVolume.config.create }}
{{- default (printf "%s-%s" (include "nextcloud.server.fullname" .) "config-pv") .Values.server.persistentVolume.config.name }}
{{- else }}
{{- default "default" .Values.server.persistentVolume.config.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the persistent volume claim to use
*/}}
{{- define "nextcloud.server.persistentVolumeClaimName.config" -}}
{{- if .Values.server.persistentVolumeClaim.config.create }}
{{- default (printf "%s-%s" (include "nextcloud.server.fullname" .) "config-pvc") .Values.server.persistentVolumeClaim.config.name }}
{{- else }}
{{- default "default" .Values.server.persistentVolumeClaim.config.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the persistent volume to use
*/}}
{{- define "nextcloud.server.persistentVolumeName.apps" -}}
{{- if .Values.server.persistentVolume.apps.create }}
{{- default (printf "%s-%s" (include "nextcloud.server.fullname" .) "apps-pv") .Values.server.persistentVolume.apps.name }}
{{- else }}
{{- default "default" .Values.server.persistentVolume.apps.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the persistent volume claim to use
*/}}
{{- define "nextcloud.server.persistentVolumeClaimName.apps" -}}
{{- if .Values.server.persistentVolumeClaim.apps.create }}
{{- default (printf "%s-%s" (include "nextcloud.server.fullname" .) "apps-pvc") .Values.server.persistentVolumeClaim.apps.name }}
{{- else }}
{{- default "default" .Values.server.persistentVolumeClaim.apps.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the persistent volume to use
*/}}
{{- define "nextcloud.server.persistentVolumeName.theme" -}}
{{- if .Values.server.persistentVolume.theme.create }}
{{- default (printf "%s-%s" (include "nextcloud.server.fullname" .) "theme-pv") .Values.server.persistentVolume.theme.name }}
{{- else }}
{{- default "default" .Values.server.persistentVolume.theme.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the persistent volume claim to use
*/}}
{{- define "nextcloud.server.persistentVolumeClaimName.theme" -}}
{{- if .Values.server.persistentVolumeClaim.theme.create }}
{{- default (printf "%s-%s" (include "nextcloud.server.fullname" .) "theme-pvc") .Values.server.persistentVolumeClaim.theme.name }}
{{- else }}
{{- default "default" .Values.server.persistentVolumeClaim.theme.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the persistent volume to use
*/}}
{{- define "nextcloud.server.persistentVolumeName.data" -}}
{{- if .Values.server.persistentVolume.data.create }}
{{- default (printf "%s-%s" (include "nextcloud.server.fullname" .) "data-pv") .Values.server.persistentVolume.data.name }}
{{- else }}
{{- default "default" .Values.server.persistentVolume.data.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the persistent volume claim to use
*/}}
{{- define "nextcloud.server.persistentVolumeClaimName.data" -}}
{{- if .Values.server.persistentVolumeClaim.data.create }}
{{- default (printf "%s-%s" (include "nextcloud.server.fullname" .) "data-pvc") .Values.server.persistentVolumeClaim.data.name }}
{{- else }}
{{- default "default" .Values.server.persistentVolumeClaim.data.name }}
{{- end }}
{{- end }}
