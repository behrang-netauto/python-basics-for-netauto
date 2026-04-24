# IOS XE Telemetry Pipeline

## Project position in the repository
- **Baseline project:** `07_snmp_cpu_monitoring_pipeline`
- **Next-generation project:** `08_iosxe_telemetry_pipeline/`

This telemetry project is the next-generation, model-driven monitoring workflow that follows the earlier SNMP-based baseline monitoring workflow.

## Current project status
The project is organized into three phases:

- **Phase 1 — Baseline telemetry pipeline** ✅ complete
- **Phase 2 — Alerting** ⏳ next
- **Phase 3 — Hardening (TLS)** ⏳ later

This README reflects the successful completion of **Phase 1**.

---

## Phase 1 goal
Build and validate a working **IOS XE model-driven telemetry pipeline** with evidence-backed execution.

Phase 1 scope:
- bring up the collector stack
- validate the receiver path from device to collector
- validate **CPU periodic telemetry** end-to-end
- validate **interface state telemetry** with **on-change** updates
- collect execution evidence

---

## Architecture used in Phase 1
**Mode:** configured dial-out subscription  
**Transport:** gRPC  
**Receiver protocol on device:** `grpc-tcp`  
**Encoding:** `encode-kvgpb`  
**Collector plugin:** `inputs.cisco_telemetry_mdt`

### Data flow
`IOS XE device -> Telegraf -> InfluxDB -> Grafana`

### Stack
- **Telegraf** = telemetry receiver / collector
- **InfluxDB 2** = storage
- **Grafana** = visualization
- **Mailpit** = reserved for Phase 2 alerting tests

### Platform used in Phase 1
- **Cat9000v**
- **CSR1000v**
- **Ubuntu collector host**

---

## Phase 1 design decisions
### CPU stream
- periodic telemetry
- one-minute CPU path used for stable visualization
- used to prove the first end-to-end green path

### Interface stream
- on-change telemetry
- interface subtree path validated first
- then verified using `shutdown / no shutdown`
- evidence collected from InfluxDB query output

### Receiver design
- Named receiver on platforms that supported it:
  - `RCVR-TELEGRAF-GRPC`
- Subscription-level receiver on platforms where global named receiver behavior differed, this was a platform-behavior difference observed in lab validation.

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

## Evidence-backed execution
Phase 1 was closed only after evidence was collected for both the collector side and the device side.

### Evidence captured
#### Collector logs
- Compose service status
- InfluxDB health output
- Telegraf live and captured logs

#### Device CLI evidence
- CPU periodic subscription verification output
- Interface on-change subscription verification output

#### Screenshots
- InfluxDB datasource and bucket validation
- CPU periodic visibility in InfluxDB and Grafana
- Before/after evidence for interface on-change behavior

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

---

## Runtime stack notes
### Docker volumes
- `influxdb2-data` persists InfluxDB data
- `grafana-data` persists Grafana state

### Telegraf output path
Telegraf writes to InfluxDB v2 using the standard `outputs.influxdb_v2` output plugin.

### Grafana usage in Phase 1
Grafana was used primarily for:
- datasource validation
- CPU panel visualization

For interface on-change validation, **InfluxDB raw/query evidence** was treated as stronger proof than Grafana charts.

---

## Phase 1 completion criteria
Phase 1 is considered complete because all of the following were achieved:
- collector stack is operational
- device receivers are connected
- CPU periodic telemetry is visible end-to-end
- interface on-change updates are visible after state change events
- execution evidence has been collected and stored

---

## Next steps
### Phase 2 — Alerting
Planned scope:
- CPU alert rule
- interface down alert rule
- SMTP path to Mailpit
- alert evidence collection

### Phase 3 — Hardening
Planned scope:
- TLS enablement
- certificate handling
- telemetry re-validation under hardened transport

---

## Summary
This project has successfully established a **working IOS XE model-driven telemetry baseline pipeline** using:
- configured dial-out subscriptions
- gRPC transport
- Telegraf as the collector
- InfluxDB as storage
- Grafana for visualization

Phase 1 is complete and evidence-backed. The next step is alerting.
