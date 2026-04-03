# NetBox Inventory Contract

## purpose
Define exactly what NetBoxInventoryProvider reads from NetBox and what shape it returns to the orchestrator.

## read fields from NetBox
For each device, the provider reads:

- `device.name`
- `device.status`
- `device.site.name`
- `device.platform.slug`
- `device.device_type.model`
- `device.primary_ip4.address`
- `device.custom_fields.upgrade_candidate`
- `device.custom_fields.transfer_method`

## normalization rules
- `inventory_hostname` = `device.name`
- `host` = IP portion of `device.primary_ip4.address` (CIDR stripped)
- `port` = `22` (provider default in v1; not read from NetBox)
- `os` = `device.platform.slug`
- `platform` = `device.platform.slug` (kept in v1 for downstream compatibility)
- `device_type` = `device.device_type.model`
- `upgrade_candidate` = `device.custom_fields.upgrade_candidate`
- `transfer_method` = `device.custom_fields.transfer_method`

## required field set for selected devices
For any device with `upgrade_candidate=true`, these fields are mandatory:
- `name`
- `platform.slug`
- `device_type.model`
- `primary_ip4.address`
- `transfer_method`

If any required field is missing, the provider must raise a validation failure.

## output shape
Example provider output:

```json
{
  "inventory_hostname": "R1",
  "host": "192.168.56.20",
  "port": 22,
  "os": "iosxe",
  "platform": "iosxe",
  "device_type": "Cisco Catalyst 8000V",
  "upgrade_candidate": true,
  "transfer_method": "scp"
}
