

# Trivy Docker Image Scan Report
Generated at: {{ now }}


---

{{- $_ := set $. "vulnCount" 0 }}
{{- range . }}
{{- if .Vulnerabilities }}
## Target: {{ .Target }}
{{- end}}

{{- if .Vulnerabilities }}
{{- $_ := set $. "vulnCount" (add $.vulnCount (len .Vulnerabilities)) }}
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

{{- if eq $.vulnCount 0 }}
✅ **No vulnerabilities found.**
{{- else }}
⚠️ **{{ $.vulnCount }} vulnerabilities found.**
{{- end }}