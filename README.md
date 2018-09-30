Determine if Ikea tradfri bulbs is are powered on (alive) or unreachable.
I don't know if there's better method, but this work fine. I used warmth because it doesn't noticeably influence the bulb state if it is powered on. Changing brightness would turn on the bulb, if if is powered on and in OFF state on the gateway. In my tests, the true alive status was determined after 6 seconds. The loop runs to 10 seconds to make sure. I also tried just changing the warmth once, but then it would take full 10 seconds to get the true status.

    1. GET coaps://IP_ADDRESS:5684/15001/BULB_DEVICE_ID and extract warmth value from reply
    2. PUT warmth - 1 (1 if warmth == 0) to the above URL
    3. wait 1 second
    4. PUT warmth (original value) to the above URL
    5. wait 1 second
    6. loop 5 times to point 2

You may need to increase the number of loop interations if your gateway is slower to update the alive status for some reason. I tested it with 4 bulbs. If you have more, it may take more time.

To automate, add this line to crontab to execute it every minute:

    * * * * * /usr/bin/ikea_tradri_alive.py
    
The logfile of bulb status created in this way can be used to replay the normal bulb usage pattern by ikea_tradfi_bulbGhost.py. Add it to the crontab instead of the logger. The input data is extracted from the logfile by ikea_tradfi_log_analyze.R.
Requires libcoap from https://github.com/home-assistant/libcoap
