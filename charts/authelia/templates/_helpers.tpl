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
Create a default fully qualified name for authelia
*/}}
{{- define "authelia.fullname" -}}
{{- printf "%s-%s-server" .Release.Name .Values.global.fullname.authelia | trunc 63 | trimSuffix "-" }}
{{- end }}
