import time
import serial

#==================================================
# CONFIGURATION
#==================================================

# Communication
ARDUINO_PORT = "/dev/ttyACM0"
BAUD = 115200

IBUS_PORT = "/dev/ttyTHS1"
IBUS_BAUD = 115200

SEND_INTERVAL = 0.05    # Every 50 ms
FAILSAFE = 0.25         # 250 ms

# PWM Settings
NEUTRAL = 1500
MAX_DELTA = 100

# Controller
TURN_CHANNEL = 0
THROTTLE_CHANNEL = 1

INVERT_TURN = False
INVERT_THROTTLE = True

# ARM switch
ARM_CHANNEL = 6

ARM_THRESHOLD = 1700
ARM_STICK_DEADZONE = 0.10

# Speed switch
# Physical controller channel 6 = Python channel index 5
SPEED_CHANNEL = 5

# Speed multipliers
LOW_SPEED = 0.40
MEDIUM_SPEED = 0.70
HIGH_SPEED = 1.00

# 3-position switch thresholds
SPEED_LOW_THRESHOLD = 1250
SPEED_HIGH_THRESHOLD = 1750

# iBUS
iBUS_MIN = 1000
iBUS_MAX = 2000
iBUS_MID = 1500
DEADZONE = 0.05


#==================================================
# iBUS DECODING
#==================================================

def read_ibus(ser):
    """
    Reads packets coming from iBUS controller and 
    validates the packet.

    Returns a list of channel values if valid.
    Otherwise returns None.
    """

    while True:

        # First byte of iBUS packet should be 0x20
        first = ser.read(1)

        if not first:
            return None

        if first[0] != 0x20:
            continue

        # Second byte should be 0x40
        second = ser.read(1)

        if not second:
            return None

        if second[0] != 0x40:
            continue

        # Remaining 30 bytes of 32-byte packet
        rest = ser.read(30)

        if len(rest) != 30:
            return None

        packet = first + second + rest

        #-------------------------------------------
        # Checksum
        #-------------------------------------------

        sender_checksum = (
            packet[30] |
            (packet[31] << 8)
        )

        calculated_checksum = (
            0xFFFF - sum(packet[:30])
        ) & 0xFFFF 

        if sender_checksum != calculated_checksum:
            continue

        #-------------------------------------------
        # Decode Channels
        #-------------------------------------------

        channels = []

        # 14 channels, 2 bytes each
        for i in range(14):

            low_byte = packet[2 + (i * 2)]
            high_byte = packet[3 + (i * 2)]

            value = (
                low_byte |
                (high_byte << 8)
            )

            channels.append(value)

        return channels


#==================================================
# JOYSTICK NORMALIZATION
#==================================================

def normalize_channel(value):

    value = max(
        iBUS_MIN,
        min(iBUS_MAX, value)
    )

    normalized = (
        (value - iBUS_MID) /
        float(iBUS_MAX - iBUS_MID)
    )

    normalized = max(
        -1.0,
        min(1.0, normalized)
    )

    # Deadzone
    if abs(normalized) < DEADZONE:
        normalized = 0.0

    return normalized


#==================================================
# SPEED CONTROL
#==================================================

def get_speed_mode(value):

    # Low switch position
    if value < SPEED_LOW_THRESHOLD:
        return LOW_SPEED, "LOW"

    # Middle switch position
    elif value < SPEED_HIGH_THRESHOLD:
        return MEDIUM_SPEED, "MEDIUM"

    # High switch position
    else:
        return HIGH_SPEED, "HIGH"


#==================================================
# DRIVE CHARACTERISTICS
#==================================================

def drive_mix(throttle, turn):

    # Inversion
    if INVERT_THROTTLE:
        throttle = -throttle

    if INVERT_TURN:
        turn = -turn

    # Differential drive mixing
    left_power = throttle + turn
    right_power = throttle - turn

    # Scale if either side exceeds 100%
    maxed = max(
        1.0,
        abs(left_power),
        abs(right_power)
    )

    left_power /= maxed
    right_power /= maxed

    return left_power, right_power


#==================================================
# SEND POWER
#==================================================

def send_power(power):

    power = max(
        -1.0,
        min(1.0, power)
    )

    return int(
        round(
            NEUTRAL + (power * MAX_DELTA)
        )
    )


#==================================================
# SERIAL
#==================================================

def send_command(ser, left_power, right_power):

    left_pwm = send_power(left_power)
    right_pwm = send_power(right_power)

    command = "{},{}\n".format(
        left_pwm,
        right_pwm
    )

    try:

        ser.write(command.encode("ascii"))

    except serial.SerialTimeoutException:

        print("ERROR: Arduino serial write timeout.")
        return None, None

    except serial.SerialException as error:

        print("ERROR: Arduino serial error: {}".format(error))
        return None, None

    return left_pwm, right_pwm


def send_neutral(ser):

    try:

        ser.write(b"1500,1500\n")
        return True

    except serial.SerialTimeoutException:

        print("ERROR: Neutral command write timeout.")
        return False

    except serial.SerialException as error:

        print("ERROR sending neutral:", error)
        return False


#==================================================
# MAIN
#==================================================

def main():

    print("Initializing Arduino serial...")

    arduino = serial.Serial(
        ARDUINO_PORT,
        BAUD,
        timeout=0.1,
        write_timeout=0.5
    )

    # Give Arduino time to reset after serial connection
    time.sleep(3)

    print("Initializing iBUS serial...")

    ibus = serial.Serial(
        IBUS_PORT,
        IBUS_BAUD,
        timeout=0.02
    )

    time.sleep(3)

    print("Sending Neutral.")

    send_neutral(arduino)

    print("READY - ROVER DISARMED")

    #-----------------------------------------------
    # Timing variables
    #-----------------------------------------------

    last_packet_time = time.monotonic()
    last_send_time = 0.0
    last_failsafe_send = 0.0

    #-----------------------------------------------
    # Arming state
    #-----------------------------------------------

    armed = False
    arm_switch_seen_off = False

    try:

        while True:

            channels = read_ibus(ibus)
            current_time = time.monotonic()

            #================================================
            # VALID iBUS PACKET
            #================================================

            if channels is not None:

                last_packet_time = current_time

                #--------------------------------------------
                # Read channels
                #--------------------------------------------

                turn_raw = channels[TURN_CHANNEL]
                throttle_raw = channels[THROTTLE_CHANNEL]
                arm_raw = channels[ARM_CHANNEL]

                # Read 3-position speed switch
                speed_raw = channels[SPEED_CHANNEL]

                turn = normalize_channel(turn_raw)
                throttle = normalize_channel(throttle_raw)

                # Determine selected speed setting
                speed_scale, speed_mode = get_speed_mode(speed_raw)

                #--------------------------------------------
                # Determine arm switch position
                #--------------------------------------------

                arm_switch_on = arm_raw >= ARM_THRESHOLD

                #================================================
                # DISARM
                #================================================

                if not arm_switch_on:

                    # We have seen the physical switch OFF.
                    # This allows a future arm.
                    arm_switch_seen_off = True

                    if armed:
                        armed = False
                        print("ROVER DISARMED")

                #================================================
                # ARM
                #================================================

                else:

                    # Only arm if:
                    # 1. Currently disarmed
                    # 2. Switch has previously been OFF
                    # 3. Throttle is centered
                    # 4. Steering is centered

                    if not armed:

                        if (
                            arm_switch_seen_off
                            and abs(throttle) <= ARM_STICK_DEADZONE
                            and abs(turn) <= ARM_STICK_DEADZONE
                        ):

                            armed = True

                            print("====================")
                            print("ROVER ARMED")
                            print("====================")

                #================================================
                # DRIVE COMMAND
                #================================================

                if armed:

                    left_power, right_power = drive_mix(
                        throttle,
                        turn
                    )

                    # Apply selected speed setting
                    left_power *= speed_scale
                    right_power *= speed_scale

                else:

                    # Always neutral while disarmed
                    left_power = 0.0
                    right_power = 0.0

                #================================================
                # SEND TO ARDUINO
                #================================================

                if current_time - last_send_time >= SEND_INTERVAL:

                    left_pwm, right_pwm = send_command(
                        arduino,
                        left_power,
                        right_power
                    )

                    if left_pwm is None:

                        print("ARDUINO COMMUNICATION LOST")

                    else:

                        state = "ARMED" if armed else "DISARMED"

                        print(
                            "{} | ARM:{} | "
                            "SPEED:{} | "
                            "Turn:{:+.2f} Throttle:{:+.2f} | "
                            "L:{} R:{}".format(
                                state,
                                arm_raw,
                                speed_mode,
                                turn,
                                throttle,
                                left_pwm,
                                right_pwm
                            )
                        )

                    last_send_time = current_time

            #================================================
            # iBUS FAILSAFE
            #================================================

            if current_time - last_packet_time > FAILSAFE:

                # Losing the controller automatically disarms
                # the rover.
                if armed:

                    armed = False
                    print("SIGNAL LOST - ROVER DISARMED")

                # Require switch OFF before allowing another arm.
                arm_switch_seen_off = False

                # Send neutral periodically while signal is lost.
                if current_time - last_failsafe_send >= SEND_INTERVAL:

                    send_neutral(arduino)
                    last_failsafe_send = current_time


    except KeyboardInterrupt:

        print("\nStopping rover...")


    finally:

        if send_neutral(arduino):
            print("Neutral sent.")
        else:
            print("WARNING: Could not send final neutral command.")

        ibus.close()
        arduino.close()

        print("Serial ports closed.")


#==================================================
# START
#==================================================

if __name__ == "__main__":
    main()
