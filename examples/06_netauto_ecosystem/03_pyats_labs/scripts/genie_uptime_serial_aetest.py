
from genie.testbed import load
from pyats import aetest
import logging
#logging.basicConfig(
#    level=logging.WARNING,
#    format="%(levelname)s %(name)s: %(message)s"
#)
log = logging.getLogger(__name__)
#log.setLevel(logging.WARNING)

SHOW_CMD = "show version"

class CommonSetup(aetest.CommonSetup):

    @aetest.subsection
    def load_testbed(self, testbed_file: str | None = None):
        try:
            self.parent.parameters["testbed"] = load(testbed_file)
        except Exception:
            self.failed("No testbed or testbed_file was accessible!!!!")
        
    @aetest.subsection
    def connect_all_devices(self, testbed):
        failed_devices = []
        failed_names = set()

        for dev_name, dev in testbed.devices.items():
            try:
                dev.connect(via="cli", log_stdout=False, timeout=10, learn_hostname=True)
            except Exception as e:
                failed_devices.append(f"{dev_name}: {type(e).__name__}: {e}")
                failed_names.add(dev_name)

        self.parent.parameters["connect_failed"] = failed_devices
        self.parent.parameters["connect_failed_names"] = failed_names
        
        if len(failed_names) == len(testbed.devices):
            self.failed("All device connections failed.\n" + "\n".join(failed_devices))

class UptimeTestcase(aetest.Testcase):

    @aetest.test
    def parse_uptime(self, testbed, connect_failed_names=None):
        result = []
        ok = 0
        errors = []

        for dev_name, dev in testbed.devices.items():
            if dev_name in connect_failed_names:
                errors.append(f"Skipping device {dev_name} due to connection failure.")
                continue

            try:
                parsed = dev.parse(SHOW_CMD)
                up_time = parsed["version"].get("uptime", "N/A")

                if up_time != "N/A":
                    result.append((dev_name, up_time))
                    ok += 1
                    log.info(f"Device {dev_name} Uptime: {up_time}")
                else:
                    errors.append(f"Uptime not found for device {dev_name}")
                    log.error(f"Uptime not found for device {dev_name}")
                
            except Exception as e:
                errors.append(f"parse error: {dev_name} - {type(e).__name__}: {e}\n")
                log.error(f"parse error: {dev_name} - {type(e).__name__}: {e}")
            
        if ok >= 1 and errors:
            self.passx(f"Some devices failed to parse: {ok} OK, {len(errors)} Failed")
        elif ok >= 1:
            self.passed(f"\nUptime parsed on {ok} devices successfully")
        else:
            self.failed("\nNo devices were parsed.")

class CommonCleanup(aetest.CommonCleanup):

    @aetest.subsection
    def disconnect_all_devices(self,testbed):
        for _, dev in testbed.devices.items():
            try:
                dev.disconnect()
            except Exception:
                pass
    