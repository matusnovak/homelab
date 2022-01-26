{{/*
Create a default fully qualified name for openldap
*/}}
{{- define "openldap.fullname" -}}
{{- printf "%s-%s" .Release.Name .Values.global.fullname.openldap | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified name for postgres
*/}}
{{- define "postgres.fullname" -}}
{{- printf "%s-%s" .Release.Name .Values.global.fullname.postgres | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified name for traefik
*/}}
{{- define "traefik.fullname" -}}
{{- printf "%s-%s" .Release.Name .Values.global.fullname.traefik | trunc 63 | trimSuffix "-" }}
{{- end }}
