# CPU fan findings — 2026-11-01

Hardware: Gigabyte B85M-D3PH, BIOS F5; ITE IT8620E controller; Revenger
G-VR341 cooler, specified as a 3-pin, 12 V, 2,100 RPM fan.

## Monitoring and display

Loading the `it87` kernel module exposed `it8620/fan1` and `it8620/fan2`.
The display selects `it8620/fan1` as the CPU fan; its speed is consistent
with the cooler's rating, but the driver does not label the physical headers.
`psutil` returns empty fan labels, so the custom sensor supplies `fan1`,
`fan2`, etc. from their enumeration order. Without a reading, it shows `--`.

The CPU panel displays a centered number below `FAN RPM`, alongside LOAD.
Both labels use 12-point text. The load value is shifted left to fit the art.
The number is raw RPM, not a percentage or a smoothed estimate.

Occasional readings near 4,400 RPM were interspersed with readings around
2,100–2,300 RPM. These near-double readings suggest tachometer/reporting
noise; they do not establish actual fan acceleration or automatic control.

## Manual control tests

The initial probe and a longer repeat tested channels 1, 2, and 3 separately.
Each channel was switched to manual mode and commanded to 100%, then 60%,
then 100%. All other channels retained their automatic settings.

The repeat sampled every two seconds for 10 seconds at full output,
16 seconds at 60%, and 10 seconds at full output again. Median readings:

| Channel | Fan | First 100% | 60% | Final 100% |
| --- | --- | ---: | ---: | ---: |
| 1 | fan1 (selected CPU fan) | 2,272 | 2,217.5 | 2,272 |
| 2 | fan2 (presumed case fan) | 1,165 | 1,073 | 1,159 |
| 3 | fan1 | 2,280 | 2,210.5 | 2,242 |

Values are RPM. CPU fan changes were small relative to the existing reading
variation; no clear control response was demonstrated. Fan2 responded
consistently to channel 2. This establishes ineffective CPU fan control in
the tested configuration, not that every possible BIOS setting or header
on this motherboard lacks DC control.

The repeat peaked at 53°C. Both tests restored all tested channels to their
original settings: `pwmN_enable=2` (automatic) and `pwmN=70`.
Automatic mode being enabled does not prove effective control of a 3-pin fan.

Raw data: [initial probe](fan-probe-2026-11-01.json) and
[longer repeat](fan-retest-2026-11-01.json). No persistent fan curve changes
were made.

After the BIOS-profile reboot, RPM disappeared because `it87` had not been
configured to load at boot. This was fixed by installing
`/etc/modules-load.d/mero-monitor.conf` with `it87` and loading the module.
The repository service installer now installs this file and loads the driver.

### BIOS Silent profile check

After selecting Silent in BIOS, `pwm1_auto_slope` changed from 28 to 16;
`pwm1_enable` remained 2. The BIOS profile therefore changed controller
configuration. A further test compared Silent automatic mode with forced
outputs, then restored Silent:

| Phase | Median fan1 RPM |
| --- | ---: |
| Silent before | 2,149 |
| Manual 100% | 2,295 |
| Manual 60% | 2,299 |
| Manual 100% again | 2,303 |
| Silent after | 2,303 |

There was no repeatable CPU fan reduction attributable to Silent: after
restoration it matched the full-output reading, and manual 60% matched 100%.
This does not prove that the board lacks DC hardware; it shows that the
Silent profile did not demonstrate useful speed control in this setup.
The test restored `pwm1=70`, `pwm1_enable=2`, retaining Silent's slope of 16.
See [Silent test readings](fan-silent-test-2026-11-01.json).

## DC support remains unresolved

[Gigabyte's specifications](https://www.gigabyte.com/br/Motherboard/GA-B85M-D3PH-rev-11/sp)
list CPU/system fan control, conditional on the installed cooler, without
explicitly promising DC voltage control. The
[available board manual](https://download.gigabyte.com/FileList/Manual/mb_manual_ga-b85m-d3ph_e.pdf)
does not establish a DC/PWM selector. The
[Linux driver documentation](https://docs.kernel.org/hwmon/it87.html)
describes the controller interface; it cannot establish the board's physical
fan-header wiring.

A 3-pin fan needs supply-voltage control to vary its speed; it cannot use
a separate fourth-pin PWM signal. The remaining check is to inspect BIOS
for a CPU fan Voltage/DC mode and, if present, repeat the test in that mode.
The current results do not justify claiming either confirmed DC support or
confirmed absence of DC hardware.

## Sensor check

From the repository root:

```bash
rtk python3 -m unittest discover -s tests
```
