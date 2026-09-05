# Autonomous Rover Testbed

A four-wheel skid-steer rover designed as a safe, modular, and repeatable platform for future autonomous control, machine-learning, and sim-to-real testing.

The system combines an **NVIDIA Jetson Nano** for high-level control with an **Arduino Mega** for low-level motor control. It also includes wireless manual control, custom mechanical integration, independent control and drivetrain power paths, layered software failsafes, and a physical emergency-stop system.

---

## Project Overview

Autonomous control software eventually needs to be tested outside simulation, where real-world effects such as wheel slip, motor behavior, communication latency, sensor noise, and changing environments become important.

This rover was built as a physical testbed for that stage of development. The completed platform currently supports reliable manual control while providing the mechanical, electrical, and software framework needed for future autonomous control and perception systems.

### Key Features

- Four-wheel-drive skid-steer drivetrain
- NVIDIA Jetson Nano for high-level control
- Arduino Mega for low-level PWM motor control
- FlySky FS-i6S transmitter and FS-iA6B receiver
- iBUS wireless command processing
- USB serial communication between Jetson and Arduino
- Four Koors40 motor controllers
- Four AndyMark RedLine motors
- Custom 3D-printed component mounts
- Modular sensor mounting platform
- Separate control-system and drivetrain power paths
- Relay-based emergency stop
- Remote software arming and disarming
- Wireless-input timeout
- Jetson-to-Arduino communication timeout
- Arduino output limiting
- Three selectable manual speed modes

---

## System Architecture

```text
FlySky FS-i6S Controller
          |
       2.4 GHz
          |
          v
FlySky FS-iA6B Receiver
          |
         iBUS
          |
          v
   NVIDIA Jetson Nano
   High-Level Control
   - Input validation
   - Arming logic
   - Speed selection
   - Skid-steer mixing
   - Command generation
          |
   USB Serial @ 115200
          |
          v
      Arduino Mega
    Low-Level Control
   - Command validation
   - Output limiting
   - Motor inversion
   - PWM generation
          |
          v
  4x Koors40 Controllers
          |
          v
      4x DC Motors
```

The electrical system is intentionally separated so drivetrain power can be disabled while the Jetson, Arduino, and receiver remain powered. This allows the operator to stop physical motion without losing access to the control computer, logs, or debugging information.

---

## Hardware

### Main Components

- **Chassis:** AndyMark Rover 8 Pneumatic
- **High-level computer:** NVIDIA Jetson Nano P3450
- **Low-level controller:** Arduino Mega
- **Motor controllers:** 4x AndyMark Koors40
- **Motors:** 4x AndyMark 775 RedLine
- **Wireless controller:** FlySky FS-i6S
- **Receiver:** FlySky FS-iA6B
- **Battery:** 12 V, 50 Ah LiFePO4
- **Main protection:** 120 A circuit breaker
- **Motor branch protection:** 4x 30 A breakers
- **Jetson regulator:** 5 V, 5 A step-down regulator
- **Emergency stop:** High-current relay controlled by a physical E-stop button

---

## Mechanical Design

The original rover chassis provided limited mounting provisions, so custom hardware was designed and iteratively prototyped in Fusion 360.

The final mechanical system includes:

- Battery and Arduino mounting system
- Main electronics mounting plate
- Raised Jetson Nano mount
- Positive and negative bus-bar mounts
- E-stop mounting structure
- Aluminum drivetrain and wiring covers
- Plexiglass structural-support clips
- Modular sensor mounting platform

The mounts were designed as separate replaceable components so future researchers can upgrade or rearrange hardware without redesigning the entire chassis.

---

## Software Architecture

### Jetson Nano — Python

The Jetson runs the high-level control program and is responsible for:

- Reading FlySky iBUS packets
- Validating packet headers and checksums
- Decoding steering, throttle, arming, and speed-mode channels
- Applying input deadzones
- Normalizing joystick values
- Generating skid-steer commands
- Applying arming logic
- Monitoring wireless-input timeout
- Sending left and right motor commands to the Arduino

Skid-steer mixing follows:

```text
left  = throttle + steering
right = throttle - steering
```

If either mixed command exceeds the normalized range, both outputs are scaled together to preserve the steering-to-throttle ratio.

### Arduino Mega — C/C++

The Arduino is responsible for low-level motor control:

- Receives left/right commands over USB serial
- Parses comma-separated PWM commands
- Rejects malformed or out-of-range values
- Applies motor-direction inversion
- Limits requested output
- Generates four stable PWM signals
- Returns all motor outputs to neutral if Jetson communication is lost

Jetson-to-Arduino command format:

```text
leftPWM,rightPWM
```

Example neutral command:

```text
1500,1500
```

PWM neutral is **1500 µs**.

The final Arduino safety limit constrains motor-controller commands to:

```text
1300 µs to 1700 µs
```

---

## Safety Systems

The rover uses multiple independent safety layers.

### Remote Arming

A controller switch acts as a software enable. When the rover is disarmed, the Jetson forces all requested motor commands to neutral.

### Wireless Timeout

If valid iBUS data is not received within the configured timeout, the Jetson sends neutral commands instead of continuing to use the last received controller position.

### Arduino Command Timeout

If the Arduino stops receiving valid commands from the Jetson, it independently returns all four motor outputs to neutral.

### Output Limiting

The Arduino applies a final PWM clamp before commands reach the motor controllers. This prevents high-level software from directly commanding the full motor-controller range.

### Physical Emergency Stop

The physical E-stop opens the high-current drivetrain path through a relay.

The Jetson and Arduino remain powered after the E-stop is activated, allowing software and debugging information to remain available after the drivetrain has been disabled.

---

## Manual Control

The FlySky controller provides:

- Steering
- Throttle
- Software arming/disarming
- Three-position speed selection

The rover supports:

- Forward motion
- Reverse motion
- Gradual turns
- Point turns

---

## Testing and Validation

Testing was performed progressively, beginning with individual subsystems before full integrated operation.

Validation included:

- Low-voltage control power
- Jetson-to-Arduino serial communication
- PWM signal quality
- Motor direction and inversion
- Forward and reverse motion
- Gradual turns
- Point turns
- Wireless steering and throttle
- Arming and disarming
- Speed modes
- Wireless receiver timeout
- Jetson-to-Arduino communication timeout
- Arduino output limiting
- Physical E-stop operation
- Full integrated manual driving

Final testing demonstrated that the rover can be:

- Manually controlled
- Remotely disarmed
- Stopped after loss of wireless input
- Stopped after loss of Jetson-to-Arduino communication
- Physically disabled at the drivetrain while keeping the control electronics powered

---

## Design Evolution

The original design attempted to generate motor-controller PWM signals directly from the Jetson Nano.

Oscilloscope testing showed that the Jetson output did not maintain a sufficiently clean PWM waveform when connected to the motor-controller input. The signal became rounded and was not reliably recognized by the controllers.

The design was revised so that:

- The **Jetson Nano** performs high-level computing and command generation.
- The **Arduino Mega** performs timing-sensitive PWM generation.

This change improved signal quality and created a cleaner separation between high-level software and low-level hardware control.

---

## Demonstration Videos

### Driving Demonstration

https://www.youtube.com/watch?v=0dPNv8tmsvw

### Emergency Stop Functionality

https://www.youtube.com/watch?v=sDpVlpVIPuo

### Additional Rover Features

https://www.youtube.com/watch?v=tUtS9Z2b58U

---

## Current Status

The rover's mechanical, electrical, communication, safety, and manual-control systems have been integrated and validated.

The platform is currently a **manual-control autonomous testbed**. Full autonomous perception and control software is intended for future development.

---

## Future Work

Planned or recommended future improvements include:

- Add perception and localization sensors
- Integrate autonomous control algorithms
- Integrate machine-learning systems
- Perform extended reliability testing
- Measure electronics temperatures during sustained operation
- Automatically launch the Jetson control software at startup
- Enable remote network access to the Jetson
- Continue sim-to-real testing and calibration

---

## Suggested Repository Structure

```text
Autonomous-Rover-Testbed/
|
|-- README.md
|-- .gitignore
|
|-- jetson/
|   `-- rover_control.py
|
|-- arduino/
|   `-- rover_motor_controller.ino
|
|-- cad/
|   |-- stl/
|   `-- step/
|
|-- schematics/
|   |-- power_architecture.pdf
|   `-- control_architecture.pdf
|
|-- images/
|   |-- rover_overview.jpg
|   |-- system_architecture.png
|   `-- pwm_comparison.jpg
|
`-- docs/
    `-- Autonomous_Rover_Testbed_Final_Report.pdf
```

File names above are suggested names. Existing project files can keep their current names if preferred.

---

## Documentation

For full design decisions, mechanical integration, electrical architecture, software implementation, and testing procedures, see the final project report in the `docs/` folder.

---

## Acknowledgments

Developed in the Department of Electrical and Computer Engineering at **Lafayette College** under the guidance of **Prof. Dr. Priyank Kalgaonkar**.

---

## Repository

https://github.com/rfrobbins/Autonomous-Rover-Testbed
