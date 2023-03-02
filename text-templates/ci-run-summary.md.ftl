[#assign openIssues = statistics.openIssues.severe]
[#assign openRuleViolations = statistics.openRuleViolations.severe]
[#assign openVulnerabilities = statistics.openVulnerabilities]
[#assign hours = (statistics.executionDurationInSeconds / 3600)?floor]
[#assign minutes = ((statistics.executionDurationInSeconds % 3600) / 60)?floor]
[#assign seconds = statistics.executionDurationInSeconds % 60]
### Summary

Completed scan with ${openIssues} open issues,
${openRuleViolations} open rule violations and ${openVulnerabilities}
open vulnerabilities.

[#assign vcs = ortResult.repository.vcsProcessed]
### Details

- code repository:
  - type: ${vcs.type}
  - url: ${vcs.url}
  - revision: ${vcs.revision}
  - path: ${vcs.path}
- duration: ${hours} hours, ${minutes} minutes and ${seconds} seconds.
