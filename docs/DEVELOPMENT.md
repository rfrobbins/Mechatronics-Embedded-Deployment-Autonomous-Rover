# Software Development and Controller Channel Mapping

This document covers basic development tasks that are useful when changing the Jetson or Arduino software.

## Editing the Jetson Python Code

The main control file is:

```text
jetsonfinal.py
```

To edit it directly on the Jetson:

```bash
nano jetsonfinal.py
```

Then run the updated program with:

```bash
sudo python3 jetsonfinal.py
```

For larger changes, it may be easier to SSH into the Jetson and edit the code from a preferred development environment on another computer.

## Editing the Arduino Code

Use the **Arduino IDE** to make changes to the Arduino program.

1. Connect the Arduino Mega to a PC with USB.
2. Open the rover Arduino sketch.
3. Select the correct Arduino board.
4. Select the correct serial port.
5. Upload the code.
6. Reconnect the Arduino to the Jetson.

The USB serial device used by the Jetson can change depending on the port or connection order. The device configured in the Python program must match the Arduino's actual serial device.

## Mapping Additional Controller Switches and Buttons

The FlySky controller has additional switches and controls that can be assigned to future rover functions.

To identify which iBUS channel corresponds to a switch or button, temporarily print the decoded channel values after a valid iBUS packet is received.

For example:

```python
print(
    "CH1:", channels[0],
    "CH2:", channels[1],
    "CH3:", channels[2],
    "CH4:", channels[3],
    "CH5:", channels[4],
    "CH6:", channels[5],
    "CH7:", channels[6],
    "CH8:", channels[7],
    "CH9:", channels[8],
    "CH10:", channels[9]
)
```

> **Important:** Perform controller-channel testing with the **motors disabled** or with the rover securely lifted so the wheels cannot drive the rover.

Run the program and move only **one controller switch or control at a time**.

Example output:

```text
CH1: 1500 CH2: 1500 CH3: 1000 CH4: 1500 CH5: 1000 CH6: 1500 CH7: 1000
CH1: 1500 CH2: 1500 CH3: 1000 CH4: 1500 CH5: 1000 CH6: 1500 CH7: 2000
```

Because only `CH7` changed from `1000` to `2000`, that switch corresponds to **iBUS channel 7**.

## Python Channel Indexing

Python lists start at index zero.

Therefore:

```python
channels[0]
```

is iBUS **Channel 1**.

Likewise:

```text
iBUS Channel 1  -> channels[0]
iBUS Channel 2  -> channels[1]
iBUS Channel 3  -> channels[2]
...
iBUS Channel 10 -> channels[9]
```

Keep this offset in mind whenever adding a new switch, button, or proportional control to `jetsonfinal.py`.

## Recommended Development Workflow

When testing new functionality:

1. Keep the rover disarmed.
2. If possible, disable drivetrain power or lift the rover.
3. Print and verify the intended input channel.
4. Add the new software behavior.
5. Verify the behavior in the terminal before allowing motor commands.
6. Test at the lowest speed first.
7. Keep the E-stop accessible.
