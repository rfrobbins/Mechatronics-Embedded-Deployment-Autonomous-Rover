# Rover Operating Guide

This guide contains the full startup, operation, and shutdown procedure for the Autonomous Rover Testbed.

## Before Powering the Rover

1. Make sure the physical **E-stop is released/reset and not pressed**.
2. Check the Arduino USB connection to the Jetson.
3. Check that the Jetson barrel jack is fully connected.
4. Make sure all switches along the top of the remote control are in the fully **UP** position.
5. Keep the rover disarmed while completing setup.

## Power-Up Procedure

1. Plug in the **XT90 battery connector**.
2. Check for power/status lights on:
   - Jetson Nano
   - Arduino Mega
   - Motor controllers
   - FlySky receiver
3. If one of these devices does not appear to have power, stop and check the wiring before continuing.
4. Turn on the FlySky remote by pressing **both power buttons at the same time**.
5. The remote should automatically connect to the receiver.

## Jetson Setup

1. Plug a mouse and keyboard into the Jetson USB ports.
2. Connect a monitor to the Jetson DisplayPort.
3. Log in to the Jetson.
4. Open a terminal.
5. Run:

```bash
sudo python3 jetsonfinal.py
```

6. Once the program starts, use the terminal to monitor the controller inputs, enable state, speed mode, and motor commands.

## Driving the Rover

### Enable Switch

The switch at the **top-left of the remote control** is used to enable and disable rover motion.

- **Up:** Disabled
- **Down:** Enabled

Before enabling the rover:

- Make sure the steering and throttle controls are centered.
- Make sure the rover has enough clear space to move.
- Keep the E-stop accessible.

Move the enable switch downward to arm/enable driving.

The current enable state is displayed in the Jetson terminal.

### Speed Switch

The three-position switch immediately to the right of the enable switch controls the speed setting.

- **Fully up:** Low speed
- **Middle:** Medium speed
- **Fully down:** Maximum speed

The selected speed mode is displayed in the terminal.

### Manual Driving

Use the **right joystick** to control the rover manually.

The control software supports forward/reverse motion and steering through the rover's skid-steer drive system.

## Normal Stop

To stop driving normally:

1. Return the enable switch to the **UP** position.
2. Confirm in the terminal that the rover is disabled/disarmed.
3. Center the joystick.

## Emergency Stop

If immediate physical shutdown of the drivetrain is required, press the **E-stop**.

The E-stop removes drivetrain power while allowing the Jetson and Arduino control electronics to remain powered.

## Software Stop

To stop the Python program from the terminal, press:

```text
Ctrl + C
```

The program should send a neutral command before closing the serial connections.

## Power-Down Procedure

1. Move the enable switch to the **UP** position.
2. Center the joystick.
3. Stop the Python program with `Ctrl + C`.
4. Confirm the rover is no longer commanding motion.
5. Disconnect the XT90 battery connector.
6. Turn off the FlySky remote.

## Troubleshooting

### Rover software cannot connect to the Arduino

The Arduino USB device/port assigned by the Jetson matters for serial communication.

If the software cannot find the Arduino:

1. Check the USB cable.
2. Try reconnecting the Arduino.
3. Check which serial device the Jetson assigned.
4. Update the Arduino serial-port setting in `jetsonfinal.py` if necessary.
5. Alternatively, reconnect using the USB port expected by the current configuration.

### Remote does not appear connected

- Confirm the receiver has power.
- Confirm the remote was turned on by pressing both power buttons.
- Check the terminal for changing controller inputs.
- Power-cycle the remote/receiver if necessary.

### Inputs appear wrong

Do not drive the rover until the controller channel mapping has been verified.

See [DEVELOPMENT.md](DEVELOPMENT.md) for the controller-channel test procedure.
