upgrade_candidate:
- type: boolean
- meaning: whether the device is selected for upgrade workflow targeting

transfer_method:
- type: select
- allowed values:
  - scp
  - copy_command
**current lab default: scp
- meaning: preferred image transfer method for the device
