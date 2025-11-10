

# Trivy Docker Image Scan Report
Generated at: {{ now }}


---
{{- range . }}
{{- if .Vulnerabilities }}
## Target: {{ base .Target }}

Path: {{ .Target }}
{{- end}}

{{- if .Vulnerabilities }}
### Vulnerabilities
| Package | Vulnerability | Severity | Installed | Fixed | Title |
|----------|----------------|-----------|------------|--------|--------|
{{- range .Vulnerabilities }}
| {{ .PkgName }} | {{ .VulnerabilityID }} | {{ .Severity }} | {{ .InstalledVersion }} | {{ .FixedVersion }} | {{ .Title }} |
{{- end }}
{{- end }}

{{- if .Misconfigurations }}
### Misconfigurations
| ID | Severity | Title | Description | Resolution |
|----|-----------|--------|--------------|-------------|
{{- range .Misconfigurations }}
| {{ .ID }} | {{ .Severity }} | {{ .Title }} | {{ .Description | replace "\n" " " }} | {{ .Resolution | replace "\n" " " }} |
{{- end }}
{{- end }}


{{- end }}

