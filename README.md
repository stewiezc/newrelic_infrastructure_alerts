# newrelic_infrastructure_alerts Ansible module
Manage Alert Conditions for New Relic Infrastructure

## Docs
https://docs.newrelic.com/docs/infrastructure/new-relic-infrastructure/infrastructure-alert-conditions/rest-api-calls-new-relic-infrastructure-alerts

## Options
| parameter | required | default | choices | comments |
|-----------|----------|---------|---------|----------|
|admin_api_key|yes| | | |
|alerts_policy_name|no|||name of the alert policy to attach the condition to.|
|comparison|no| |<ul><li>above</li><li>below</li></ul><ul><li>equal</li></ul>|The value used to define the threshold. Applies to infra_metric and infra_process_running.|
|critical_threshold|no| | |defined as a dictionary with values for `duration_minutes`, `value`, and `time_function` depending on type. |
|enabled|no|True|<ul><li>True</li><li>False</li></ul>|Whether the condition is turned on or off.|
|event_type|no|||Applies to infra_metric. The metric event; for example, system metrics, process metrics, storage metrics, or network metrics. This automatically populates for Infrastructure Integrations; for example, StorageSample.|
|name|yes|||The name of your alert condition.|
|process_where_clause|no|||Applies to infra_process_running. Any filters applied to processes.|
|select_value|no|||Applies to infra_metric. Identifies the type of metric condition. Example: diskFreePercent.|
|state|no|present|<ul><li>present</li><li>absent</li></ul>|Specify whether to create or delete alert condition.|
|type|no||<ul><li>infra_process_running</li><li>infra_metric</li><li>infra_host_not_reporting</li></ul>|The type of Infrastructure alert condition.|
|warning_threshold|no|||Applies only to infra_metric conditions. Optional warning threshold.|
|where_clause|no|||Applies a host filter to the alert condition.|

## Examples
```
- name: create host not reporting alert condition
  newrelic_infrastructure_alerts:
    admin_api_key: 12345678901234567890
    name: slack_host_not_reporting_5mins
    type: infra_host_not_reporting
    alerts_policy_name: slack_alert_policy
    critical_threshold:
      duration_minutes: 5
    state: present
  register: result
```
```
- name: create disk usage alert condition 
  newrelic_infrastructure_alerts:
    admin_api_key: 12345678901234567890
    name: pagerduty_disk_used_above_90%
    type: infra_metric
    alerts_policy_name: pagerduty_alert_policy
    event_type: StorageSample
    select_value: diskUsedPercent
    comparison: above
    critical_threshold:
      value: 90
      duration_minutes: 5
      time_function: any
    state: present
  register: result
```
```
- name: process running condition
  newrelic_infrastructure_alerts:
    admin_api_key: 12345678901234567890
    name: slack_java_process_not_running
    type: infra_process_running
    alerts_policy_name: slack_alert_policy
    where_clause: (hostname LIKE '%websrv%')
    comparison: below
    critical_threshold:
      value: 1
      duration_minutes: 15
    process_where_clause: (commandName = 'java')
    state: present
  register: result
```