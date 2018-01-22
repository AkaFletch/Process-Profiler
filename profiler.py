#!/usr/bin/env python3
"""
MIT License

Copyright (c) 2018 Matthew Threlfall

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import subprocess, datetime, sys, argparse


parser = argparse.ArgumentParser(description='Will track the CPU and Memory usage through top along with Nvidia GPU usage using nvidia-smi', epilog='Nvidia-Jetson boards have limited support')

parser.add_argument('command', metavar='command', type=str, help='the command you wish to track the usage of')

parser.add_argument('--optirun', action='store_true', default=False, help='whether to access nvidia-smi requires the prefix optirun, for optimus GPUs')

parser.add_argument('--primusrun', action='store_true',default=False, help='whether to access nvidia-smi requires the prefix primusrun, for optimus GPUs')

parser.add_argument('--output', action='store', help='the path to the output file')

#TODO @FletchDev ensure it runs with sudo permissions
parser.add_argument('--jetson', action='store', help='the path to tegra-stats')

parser.add_argument('--nogpu', action='store_true', help='do not track GPU usage')

args = parser.parse_args()

columns = ['CPU','Memory']

nvidiaColumns = ['fan', 'temp', 'perf', 'power usage', 'mem used', 'mem total', 'gpu util']

def removeBytes(string):
    return str(string).replace('b', '').replace('\'', '').replace('\\n','')

def getGpu(pid):
	if args.nogpu:
		return ""
	elif args.jetson:
		return getJetsonGpu()
	else:
		return getNvidGpu(pid)

#TODO @FletchDev
def getJetsonGpu():
	gpu = subprocess.Popen('todo', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	while len(gpu.stdout.readlines()) < 1:
		pass
	return "todo"

#TODO @FletchDev better formatting
def getNvidGpu(pid):	
	prefix = ''
	if args.optirun:
		prefix = 'optirun'
	elif args.primusrun:
		prefix = 'primusrun'
	print(prefix)
	nvidiasmi = subprocess.Popen(prefix + ' nvidia-smi', shell=True,
		stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	d = nvidiasmi.stdout.readlines()[8].split()
	d = list(map(removeBytes, d))
	return d[1] +', '+ d[2] +', '+d[4] +', '+d[6] +', '+ d[8] +', '+ d[10] +', '+ d[12] 
	

prefix = ''
if args.optirun:
	prefix = 'optirun'
elif args.primusrun:
	prefix = 'primusrun'
nvidiatest = subprocess.Popen(prefix + ' nvidia-smi', shell=True,
				stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

testResult = str(nvidiatest.stdout.readlines())

if testResult[0].startswith('NVIDIA-SMI has failed because it couldn'):
	print("nvidia-smi failed: could\'t communicate to the nvidia drivers")
	print("are you using bumblebee? use --primusrun or --optirun to use these prefixes")
	quit(-1)
elif len(testResult) < 43:
	print("Bash has failed to find " + prefix + " nvidia-smi")
	print("Are the nvidia Drivers setup correctly?")
	quit(-1)

#TODO @FletchDev add print the command here
print('Starting command ' + args.command + " at "+ str(datetime.datetime.now().time()))
pid = subprocess.Popen(args.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
print(pid.pid)
print(columns + nvidiaColumns)
lastTime = datetime.datetime.now()

while pid.poll()==None:
	top = subprocess.Popen('top -n 1 -p ' + str(pid.pid), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	topData = removeBytes(str(top.stdout.readlines()[7])).split()
	print(topData[5] + "," + topData[8] + "," +topData[9] + "," + str(getGpu(pid.pid)))

	while (datetime.datetime.now()-lastTime).seconds < 1:
		pass
	lastTime = datetime.datetime.now()
