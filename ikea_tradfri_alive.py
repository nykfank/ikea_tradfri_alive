#!/usr/bin/python
# Determine if Ikea tradfri bulbs is are powered on (alive) or unreachable.
api_ip = "192.168.1.135" # IP address of Ikea tradfri gateway
api_user = 'nyk' # API user for PSK
psk = 'J0cdsbHYCwbWDGnN' # Pre-shared key from 15011/9063 with {"9090":"api_user"} payload
bulb_ids = 65538, 65541, 65542, 65544 # Device IDs of bulb to check
logfile = '/opt/tradfri.txt' # Path of logfile
coap_path = '/usr/local/bin/coap-client' # Path of coap-client binary

import subprocess, json, time

def getStatus(bulb_id):
	cmd = coap_path, '-m', 'get', '-u', api_user, '-k', psk, 'coaps://%s:5684/15001/%d' % (api_ip, bulb_id)
	p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = p.communicate()
	outj = json.loads(out)
	alive = outj['9019']
	dimmer = outj['3311'][0]
	power, brightness, warmth = dimmer['5850'], dimmer['5851'], dimmer['5711']
	return alive, power, brightness, warmth

def setWarmth(bulb_id, warmth):
	cmd = coap_path, '-m', 'put', '-u', api_user, '-k', psk, 'coaps://%s:5684/15001/%d' % (api_ip, bulb_id)
	cmd += '-e', '{ "3311": [{ "5711": %d }] }' % warmth
	p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = p.communicate()

def changeWarmth(warmth):
	if warmth > 0: return warmth - 1
	return 1

def checkAlive(test_bulb):
	alive0, power0, brightness0, warmth0 = getStatus(test_bulb)
	for i in range(5):
		setWarmth(test_bulb, changeWarmth(warmth0))
		time.sleep(1)
		setWarmth(test_bulb, warmth0)
		time.sleep(1)
		alive, power, brightness, warmth = getStatus(test_bulb)
	return alive, power, brightness, warmth

for test_bulb in bulb_ids:
	alive, power, brightness, warmth = checkAlive(test_bulb)
	logstring = '\t'.join(map(str, (int(time.time()), test_bulb, alive, power, brightness, warmth)))
	print logstring
	open(logfile, 'a').write(logstring + '\n')
