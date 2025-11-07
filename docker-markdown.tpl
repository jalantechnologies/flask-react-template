

# Trivy Docker Image Scan Report
Generated at: {{ now }}


---
{{- $found := false }}
{{- range . }}
{{- if .Vulnerabilities }}
## Target: {{ .Target }}
{{- end}}

{{- if .Vulnerabilities }}
    {{- $found = true }}
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

{{- if not $.found }}
✅ **No vulnerabilities found.**
{{- end }}