#!/usr/bin/python
# Determine if Ikea tradfri bulbs is are powered on (alive) or unreachable.
import subprocess, json, time
cfg = json.load(open("/opt/ikea_tradfri_config.txt"))

def getBulbs():
	cmd = cfg['coap_path'], '-m', 'get', '-u', cfg['api_user'], '-k', cfg['psk'], 'coaps://%s:5684/15001' % cfg['api_ip']
	p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = p.communicate()
	bulb_ids = []
	for bulb_id in json.loads(out):
		cmd = cfg['coap_path'], '-m', 'get', '-u', cfg['api_user'], '-k', cfg['psk'], 'coaps://%s:5684/15001/%d' % (cfg['api_ip'], bulb_id)
		p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		out, err = p.communicate()
		outj = json.loads(out)
		if outj['3']['1'].find('bulb') >= 0: bulb_ids.append(bulb_id)
	return bulb_ids

def getStatus(bulb_id):
	cmd = cfg['coap_path'], '-m', 'get', '-u', cfg['api_user'], '-k', cfg['psk'], 'coaps://%s:5684/15001/%d' % (cfg['api_ip'], bulb_id)
	p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = p.communicate()
	outj = json.loads(out)
	alive = outj['9019']
	dimmer = outj['3311'][0]
	power, brightness, warmth = dimmer['5850'], dimmer['5851'], dimmer['5711']
	return alive, power, brightness, warmth

def setWarmth(bulb_id, warmth):
	cmd = cfg['coap_path'], '-m', 'put', '-u', cfg['api_user'], '-k', cfg['psk'], 'coaps://%s:5684/15001/%d' % (cfg['api_ip'], bulb_id)
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

bulb_ids = getBulbs()
for test_bulb in bulb_ids:
	alive, power, brightness, warmth = checkAlive(test_bulb)
	logstring = '\t'.join(map(str, (int(time.time()), test_bulb, alive, power, brightness, warmth)))
	print logstring
	open(cfg['logfile'], 'a').write(logstring + '\n')
