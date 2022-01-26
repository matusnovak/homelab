{{/*
Expand the name of the chart.
*/}}
{{- define "nextcloud.onlyoffice.name" -}}
{{- default (printf "%s-onlyoffice" .Chart.Name) .Values.onlyoffice.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "nextcloud.onlyoffice.fullname" -}}
{{- printf "%s-%s-onlyoffice" .Release.Name .Values.global.fullname.nextcloud | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "nextcloud.onlyoffice.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "nextcloud.onlyoffice.labels" -}}
helm.sh/chart: {{ include "nextcloud.onlyoffice.chart" . }}
{{ include "nextcloud.onlyoffice.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "nextcloud.onlyoffice.selectorLabels" -}}
app.kubernetes.io/name: {{ include "nextcloud.onlyoffice.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "nextcloud.onlyoffice.serviceAccountName" -}}
{{- if .Values.onlyoffice.serviceAccount.create }}
{{- default (include "nextcloud.onlyoffice.fullname" .) .Values.onlyoffice.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.onlyoffice.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the role to use
*/}}
{{- define "nextcloud.onlyoffice.roleName" -}}
{{- if .Values.onlyoffice.role.create }}
{{- default (include "nextcloud.onlyoffice.fullname" .) .Values.onlyoffice.role.name }}
{{- else }}
{{- default "default" .Values.onlyoffice.role.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the persistent volume to use
*/}}
{{- define "nextcloud.onlyoffice.persistentVolumeName.data" -}}
{{- if .Values.onlyoffice.persistentVolume.data.create }}
{{- default (printf "%s-%s" (include "nextcloud.onlyoffice.fullname" .) "data-pv") .Values.onlyoffice.persistentVolume.data.name }}
{{- else }}
{{- default "default" .Values.onlyoffice.persistentVolume.data.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the persistent volume claim to use
*/}}
{{- define "nextcloud.onlyoffice.persistentVolumeClaimName.data" -}}
{{- if .Values.onlyoffice.persistentVolumeClaim.data.create }}
{{- default (printf "%s-%s" (include "nextcloud.onlyoffice.fullname" .) "data-pvc") .Values.onlyoffice.persistentVolumeClaim.data.name }}
{{- else }}
{{- default "default" .Values.onlyoffice.persistentVolumeClaim.data.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the persistent volume to use
*/}}
{{- define "nextcloud.onlyoffice.persistentVolumeName.logs" -}}
{{- if .Values.onlyoffice.persistentVolume.logs.create }}
{{- default (printf "%s-%s" (include "nextcloud.onlyoffice.fullname" .) "logs-pv") .Values.onlyoffice.persistentVolume.logs.name }}
{{- else }}
{{- default "default" .Values.onlyoffice.persistentVolume.logs.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the persistent volume claim to use
*/}}
{{- define "nextcloud.onlyoffice.persistentVolumeClaimName.logs" -}}
{{- if .Values.onlyoffice.persistentVolumeClaim.logs.create }}
{{- default (printf "%s-%s" (include "nextcloud.onlyoffice.fullname" .) "logs-pvc") .Values.onlyoffice.persistentVolumeClaim.logs.name }}
{{- else }}
{{- default "default" .Values.onlyoffice.persistentVolumeClaim.logs.name }}
{{- end }}
{{- end }}
