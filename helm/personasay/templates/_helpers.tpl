{{/*
Expand the name of the chart.
*/}}
{{- define "personasay.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "personasay.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "personasay.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "personasay.labels" -}}
helm.sh/chart: {{ include "personasay.chart" . }}
{{ include "personasay.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "personasay.selectorLabels" -}}
app.kubernetes.io/name: {{ include "personasay.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Backend specific labels
*/}}
{{- define "personasay.backend.labels" -}}
{{ include "personasay.labels" . }}
app.kubernetes.io/component: backend
{{- end }}

{{/*
Backend selector labels
*/}}
{{- define "personasay.backend.selectorLabels" -}}
{{ include "personasay.selectorLabels" . }}
app.kubernetes.io/component: backend
{{- end }}

{{/*
Frontend specific labels
*/}}
{{- define "personasay.frontend.labels" -}}
{{ include "personasay.labels" . }}
app.kubernetes.io/component: frontend
{{- end }}

{{/*
Frontend selector labels
*/}}
{{- define "personasay.frontend.selectorLabels" -}}
{{ include "personasay.selectorLabels" . }}
app.kubernetes.io/component: frontend
{{- end }}

{{/*
Create the name of the service account to use for backend
*/}}
{{- define "personasay.backend.serviceAccountName" -}}
{{- if .Values.backend.serviceAccount.create }}
{{- default (printf "%s-backend" (include "personasay.fullname" .)) .Values.backend.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.backend.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the service account to use for frontend
*/}}
{{- define "personasay.frontend.serviceAccountName" -}}
{{- if .Values.frontend.serviceAccount.create }}
{{- default (printf "%s-frontend" (include "personasay.fullname" .)) .Values.frontend.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.frontend.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Merge global and component-specific environment variables
*/}}
{{- define "personasay.backend.env" -}}
{{- $globalEnv := .Values.global.env | default dict }}
{{- $backendEnv := .Values.backend.env | default dict }}
{{- merge $backendEnv $globalEnv | toYaml }}
{{- end }}

