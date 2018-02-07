# newrelic_infrastructure_alerts Ansible module
Manage Alert Conditions for New Relic Infrastructure

## Docs
https://docs.newrelic.com/docs/infrastructure/new-relic-infrastructure/infrastructure-alert-conditions/rest-api-calls-new-relic-infrastructure-alerts

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