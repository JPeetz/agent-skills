# Changelog

## [1.0.0] - 2026-10-05

### Added
- Initial release: fsi-compliance-checker skill for PCI-DSS v4.0 and MAS TRM compliance review
- Framework selection logic with reference files for PCI-DSS and MAS TRM
- Structured review process: scope → select controls → assess → report → remediate
- Report format with per-control findings, severities, remediation, and evidence gaps
- Common FSI engineering triggers for proactive compliance checking
- Anti-rationalization table covering 7 common compliance avoidance patterns
- 3 eval cases (PCI logging violation, MAS TRM cloud migration, PAN exposure)
- Reference files: pci-dss.md (PCI-DSS v4.0 control summaries), mas-trm.md (MAS TRM 2021 summaries)