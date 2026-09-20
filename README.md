# Autonomous Rover Testbed

A four-wheel skid-steer rover built as a modular platform for manual control and future autonomous-control development.

The rover uses an **NVIDIA Jetson Nano** for high-level control and an **Arduino Mega** for low-level motor control.

## Quick Start

> **Safety:** Keep the rover disarmed while setting up. Make sure the physical E-stop is released/reset before operation, and keep it accessible whenever the drivetrain is powered.

1. Check that the Arduino USB cable is securely connected to the Jetson.
2. Check that the Jetson barrel-jack power connection is secure.
3. Make sure all switches on the top of the FlySky remote are in the fully **UP** position.
4. Connect the XT90 battery connector.
5. Confirm power/status lights are visible on the Jetson Nano, Arduino Mega, motor controllers, and FlySky receiver.
6. Turn on the remote by pressing both power buttons at the same time. It should automatically connect to the receiver.
7. Connect a keyboard and mouse to the Jetson and a monitor to the DisplayPort.
8. Log in to the Jetson and open a terminal.
9. Start the rover control program:

```bash
sudo python3 jetsonfinal.py
```

10. Confirm that controller inputs, arm state, and speed mode are being displayed in the terminal.
11. To enable driving, move the **top-left switch on the remote downward**.
12. Select a speed with the three-position switch directly to the right.

```text
UP      = Low
MIDDLE  = Medium
DOWN    = High
```

13. Use the **right joystick** to drive the rover.

To stop normal operation, return the enable switch to the **UP** position.

For emergency shutdown, use the physical **E-stop**.

## Software

### Jetson

The main control program is:

```text
jetsonfinal.py
```

Run it with:

```bash
sudo python3 jetsonfinal.py
```

To edit it directly on the Jetson:

```bash
nano jetsonfinal.py
```

You can also SSH into the Jetson and edit the file using a preferred coding platform.

### Arduino

Arduino code should be edited and uploaded using the **Arduino IDE**.

1. Disconnect the Arduino from the Jetson.
2. Connect it to a PC with USB.
3. Open the Arduino sketch in Arduino IDE.
4. Select the correct board and serial port.
5. Upload the code.
6. Reconnect the Arduino to the Jetson.

The Arduino serial device used by the Python program must match the USB port/device assigned by the Jetson.

## Documentation

Full operating guide:

```text
docs/OPERATING_GUIDE.md
```

Software development and controller channel mapping:

```text
docs/DEVELOPMENT.md
```

## Demonstration Videos

Driving Demonstration:

https://www.youtube.com/watch?v=0dPNv8tmsvw

Emergency Stop Functionality:

https://www.youtube.com/watch?v=sDpVlpVIPuo

Additional Rover Features:

https://www.youtube.com/watch?v=tUtS9Z2b58U
