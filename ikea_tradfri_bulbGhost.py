#!/usr/bin/python
# Determine if Ikea tradfri bulbs is are powered on (alive) or unreachable.
api_ip = "192.168.1.135" # IP address of Ikea tradfri gateway
api_user = 'nyk' # API user for PSK
psk = '' # Pre-shared key from 15011/9063 with {"9090":"api_user"} payload
coap_path = '/usr/local/bin/coap-client' # Path of coap-client binary
dayfile = '/opt/tradfri_day.tsv'

import subprocess, time, json

def getStatus(bulb_id):
	cmd = coap_path, '-m', 'get', '-u', api_user, '-k', psk, 'coaps://%s:5684/15001/%d' % (api_ip, bulb_id)
	p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = p.communicate()
	outj = json.loads(out)
	alive = outj['9019']
	dimmer = outj['3311'][0]
	power, brightness, warmth = dimmer['5850'], dimmer['5851'], dimmer['5711']
	return map(int, [alive, power, brightness, warmth])

def setStatus(bulb_id, power, brightness, warmth):
	cmd = coap_path, '-m', 'put', '-u', api_user, '-k', psk, 'coaps://%s:5684/15001/%d' % (api_ip, bulb_id)
	cmd += '-e', '{ "3311": [{ "5850": %d, "5851": %d, "5711": %d }] }' % (power, brightness, warmth)
	p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = p.communicate()

daySet = {}
for i in open(dayfile):
	bulb, minute, power, brightness, warmth = i.strip().split('\t')
	bulb, power, brightness, warmth = map(int, [bulb, power, brightness, warmth])
	if not daySet.has_key(bulb): daySet[bulb] = {}
	daySet[bulb][minute] = power, brightness, warmth

now = time.strftime("%H:%M", time.localtime())
for bulb in daySet.keys():
	if not daySet[bulb].has_key(now): continue
	alive0, power0, brightness0, warmth0 = getStatus(bulb)
	power, brightness, warmth = daySet[bulb][now]
	print now, bulb, power, brightness, warmth
	if power0 == 0 and power == 0: continue
	setStatus(bulb, power, brightness, warmth)
