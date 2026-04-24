# IOS XE Telemetry Pipeline

## Project position in the repository
- **Baseline project:** `07_snmp_cpu_monitoring_pipeline`
- **Next-generation project:** `08_iosxe_telemetry_pipeline`

This telemetry project is the next-generation, model-driven monitoring workflow that follows the earlier SNMP-based baseline monitoring workflow.

## Current project status
The project is organized into three phases:

- **Phase 1 — Baseline telemetry pipeline** ✅ complete
- **Phase 2 — Alerting** ✅ complete
- **Phase 3 — Hardening (TLS)** ⏳ next

This README reflects the successful completion of **Phase 1** and **Phase 2**.

---

## Project goals by phase
### Phase 1 goal
Build and validate a working **IOS XE model-driven telemetry pipeline** with evidence-backed execution.

Phase 1 scope:
- bring up the collector stack
- validate the receiver path from device to collector
- validate **CPU periodic telemetry** end-to-end
- validate **interface state telemetry** with **on-change** updates
- collect execution evidence

### Phase 2 goal
Add and validate **alerting** on top of the working telemetry baseline.

Phase 2 scope:
- create Grafana-managed alert rules
- validate a **CPU high** alert path
- validate an **interface down** alert path
- route notifications to **Mailpit** through Grafana email contact points
- collect alerting evidence

---

## Architecture used in Phases 1 and 2
**Mode:** configured dial-out subscription  
**Transport:** gRPC  
**Receiver protocol on device:** `grpc-tcp`  
**Encoding:** `encode-kvgpb`  
**Collector plugin:** `inputs.cisco_telemetry_mdt`

### Data flow
`IOS XE device -> Telegraf -> InfluxDB -> Grafana -> Mailpit`

### Stack
- **Telegraf** = telemetry receiver / collector
- **InfluxDB 2** = storage
- **Grafana** = visualization and alerting
- **Mailpit** = test SMTP sink for alert validation

### Platforms used in Phases 1 and 2
- **Cat9000v**
- **CSR1000v**
- **Ubuntu collector host**

---

## Phase 1 design decisions
### CPU stream
- periodic telemetry
- one-minute CPU path used for stable visualization on Cat9000v
- used to prove the first end-to-end green path
- CPU timing was later normalized across devices during lab validation so both platforms could be compared more easily

### Interface stream
- on-change telemetry
- interface subtree path was validated first with periodic updates
- after XPath validation, the same telemetry target was moved to **on-change**
- behavior was verified using `shutdown / no shutdown`
- evidence was collected from InfluxDB query output rather than relying only on charts

### Receiver design
- Named receiver on platforms that supported it:
  - `RCVR-TELEGRAF-GRPC`
- Subscription-level receiver on platforms where global named receiver behavior differed
- This was treated as a platform-behavior difference observed during lab execution, not as a pipeline failure

---

## Phase 2 design decisions
### Alert routing
- Grafana-managed alert rules were used
- alert notifications were sent through Grafana email integration
- **Mailpit** was used as the SMTP sink for safe lab validation

### CPU alert
- a CPU threshold rule was created for Cat9000v using the periodic CPU stream
- the alert path was validated end-to-end:
  - Grafana rule evaluation
  - alert firing state
  - email delivery to Mailpit

### Interface alert
- an interface-down alert rule was created using the interface telemetry stream
- interface state changes were converted into an alertable condition inside the query logic
- the alert path was validated end-to-end:
  - interface event generation on device
  - alert evaluation in Grafana
  - email delivery to Mailpit

### Evidence principle
Phase 2 used the same **evidence-backed execution** rule as Phase 1:
- rule creation alone was not considered success
- the phase was closed only after notification delivery was observed and captured

---

## Directory layout
```text
08_iosxe_telemetry_pipeline/
├── collector/
│   ├── telegraf/
│   │   ├── telegraf.conf
│   │   └── certs/
│   ├── influxdb/
│   │   └── init/
│   └── grafana/
│       ├── provisioning/
│       └── dashboards/
├── device_configs/
│   └── iosxe/
│       ├── cpu_periodic.txt
│       ├── interface_on_change.txt
│       ├── receiver_profile_tls.txt
│       └── notes/
├── evidence_pack/
│   ├── logs/
│   ├── sample_metrics/
│   └── screenshots/
├── docker-compose.yml
└── README.md
```

---

## What was validated in Phase 1
### Collector side
- Docker Compose stack came up successfully
- Telegraf listener came up on the expected receiver port
- InfluxDB health endpoint responded successfully
- Grafana datasource was validated successfully

### Device side
- receiver configuration validated
- configured telemetry subscriptions validated
- device receiver state reached **Connected**

### End-to-end telemetry
- CPU periodic telemetry from IOS XE reached InfluxDB
- CPU data was visualized successfully
- interface on-change telemetry produced observable updates after interface state changes

---

## What was validated in Phase 2
### Grafana alerting path
- a working email contact point was configured
- notification routing was validated
- Grafana-managed rules were created successfully

### CPU alert validation
- CPU alert rule was evaluated successfully
- CPU alert entered the expected alert state under the lab scenario
- Mailpit received the CPU alert notification

### Interface alert validation
- interface alert rule was evaluated successfully
- interface state change triggered the expected alert path
- Mailpit received the interface alert notification

### Alert evidence
- Grafana rule configuration and evaluation states were captured
- Mailpit inbox and delivered alert messages were captured
- alerting was validated against real telemetry, not mock data

---

## Evidence-backed execution
Phases 1 and 2 were closed only after evidence was collected for both the collector side and the device side, and for the alerting path.

### Evidence captured
#### Collector logs
- Compose service status
- InfluxDB health output
- Telegraf live and captured logs

#### Device CLI evidence
- CPU periodic subscription verification output
- Interface on-change subscription verification output

#### Screenshots from Phase 1
- InfluxDB datasource and bucket validation
- CPU periodic visibility in InfluxDB and Grafana
- before/after evidence for interface on-change behavior

#### Screenshots from Phase 2
- Grafana contact point and notification path
- CPU alert rule and firing behavior
- interface alert rule and firing behavior
- Mailpit inbox and delivered emails

### Evidence directory used
```text
examples/06_netauto_ecosystem/08_iosxe_telemetry_pipeline/evidence_pack/
```

Typical Phase 1 evidence includes:
- `logs/collector/phase1_compose_ps.txt`
- `logs/collector/phase1_influx_health.json`
- `logs/collector/phase1_telegraf_cpu.log`
- `logs/device_cli/IOS_XE_CPU_periodic_subscription.txt`
- `logs/device_cli/IOS_XE_if_on_change_subscription.txt`
- `screenshots/phase1/...`

Typical Phase 2 evidence includes:
- Grafana alert rule screenshots
- Grafana notification/contact point screenshots
- Mailpit alert delivery screenshots
- any exported or saved alerting logs kept under the same `evidence_pack/` structure

---

## Runtime stack notes
### Docker volumes
- `influxdb2-data` persists InfluxDB data
- `grafana-data` persists Grafana state

### Telegraf output path
Telegraf writes to InfluxDB v2 using the standard `outputs.influxdb_v2` output plugin.

### Grafana usage
Grafana was used for:
- datasource validation
- CPU panel visualization
- alert rule management
- email notification testing through Mailpit

For interface on-change validation in Phase 1, **InfluxDB raw/query evidence** was treated as stronger proof than charts.

---

## Phase 1 completion criteria
Phase 1 is considered complete because all of the following were achieved:
- collector stack is operational
- device receivers are connected
- CPU periodic telemetry is visible end-to-end
- interface on-change updates are visible after state change events
- execution evidence has been collected and stored

## Phase 2 completion criteria
Phase 2 is considered complete because all of the following were achieved:
- a working Grafana email contact point was configured
- CPU alert evaluation and notification path were validated
- interface alert evaluation and notification path were validated
- Mailpit received alert notifications
- alerting evidence has been collected and stored

---

## Next phase
### Phase 3 — Hardening (TLS)
Planned scope:
- TLS enablement
- certificate handling
- telemetry re-validation under hardened transport
- evidence collection after hardening

---

## Summary
This project has successfully established a **working IOS XE model-driven telemetry pipeline** using:
- configured dial-out subscriptions
- gRPC transport
- Telegraf as the collector
- InfluxDB as storage
- Grafana for visualization and alerting
- Mailpit for alert delivery validation

**Phase 1** established the telemetry baseline.  
**Phase 2** added and validated alerting on top of that baseline.  
The next phase is **Phase 3 hardening with TLS**.
