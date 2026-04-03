# Phase 3 Summary

## purpose
Build the minimum working NetBox data model for the lab so the orchestrator can later consume NetBox as a Source of Truth.

## scope
Phase 3 is the minimum modeling/data-entry phase.

It is intentionally limited to:
- minimum object creation
- management-only device modeling
- custom-field population needed for workflow selection

It does not yet include:
- orchestrator integration
- write-back execution
- detailed lifecycle/status taxonomy
- broader IPAM/DCIM expansion beyond the lab minimum

## modeling strategy
The lab is modeled site-first and management-first.

Current conventions:
- a single Site for the whole lab: `LAB-PRIMARY`
- a single Manufacturer: `Cisco`
- a single Platform: `iosxe`
- a single Device Role: `router`
- a single Device Type for the current lab family: `Cisco Catalyst 8000V`
- management-only interface modeling in this phase
- management interface naming convention: `Mgmt0`

## object set created
The minimum object set for Phase 3 is:

- Site
- Manufacturer
- Platform
- Device Role
- Device Type
- Device
- Interface (management only)
- IP Address (management only)
- Custom Fields:
  - `upgrade_candidate`
  - `transfer_method`

## devices modeled
The current lab device set is:

- R1
- R2
- R3
- R4
- R5

Each device is modeled with:
- site
- role
- type
- platform
- status = active
- one management interface
- one management IP
- primary IP set

## custom field intent
### `upgrade_candidate`
Boolean selector used to determine whether a device is included in workflow targeting.

### `transfer_method`
Device-level transfer preference for the upgrade workflow.

Current allowed values:
- `scp`
- `copy_command`

Current lab default:
- `scp`

## result of Phase 3
At the end of Phase 3, the lab has:

- a minimum working inventory in NetBox
- management IP mapped to each modeled device
- custom fields populated for workflow selection
- naming and modeling conventions documented
- a usable base for `NetBoxInventoryProvider`

## operational outcome
Phase 3 establishes the minimum NetBox inventory required for Phase 4 integration.

That means the next phase can:
- resolve device inventory from NetBox
- filter devices by `upgrade_candidate=true`
- use `transfer_method` as workflow metadata
- normalize NetBox records into orchestrator-ready shape

## closure statement
Phase 3 is complete when:
- all minimum objects exist
- all management interfaces and primary IPs are set
- custom fields are populated
- the lab conventions are documented
- the inventory is ready for provider-driven orchestration
