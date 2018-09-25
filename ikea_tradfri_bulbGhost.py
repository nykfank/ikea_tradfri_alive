#!/usr/bin/python
# Replay the normal bulb usage pattern
import subprocess, time, json
cfg = json.load(open("/opt/ikea_tradfri_config.txt"))

def getStatus(bulb_id):
	cmd = cfg['coap_path'], '-m', 'get', '-u', cfg['api_user'], '-k', cfg['psk'], 'coaps://%s:5684/15001/%d' % (cfg['api_ip'], bulb_id)
	p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = p.communicate()
	outj = json.loads(out)
	alive = outj['9019']
	dimmer = outj['3311'][0]
	power, brightness, warmth = dimmer['5850'], dimmer['5851'], dimmer['5711']
	return map(int, [alive, power, brightness, warmth])

def setStatus(bulb_id, power, brightness, warmth):
	cmd = cfg['coap_path'], '-m', 'put', '-u', cfg['api_user'], '-k', cfg['psk'], 'coaps://%s:5684/15001/%d' % (cfg['api_ip'], bulb_id)
	cmd += '-e', '{ "3311": [{ "5850": %d, "5851": %d, "5711": %d }] }' % (power, brightness, warmth)
	p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = p.communicate()

daySet = {}
for i in open(cfg['dayfile']):
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
