#!/usr/bin/env python
"""
Created by Milan B. (C) 2017 www.bastl.sk

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import sys
import os
import re
from optparse import OptionParser


defaults = {
'unit' : "",
'maxsize' : "5.0",
'spindle-on' : "M03 S255",
'spindle-off' : "M05",
'tool-cmd' : "",
'init-cmd' : "",
'msg-cmd' : "M117",
'drill-height':"-3",
'safe-height' : "2",
'tool-change-height' : "35",
'drill-speed' : "50",
'retract-speed' : "700",
'move-speed' : "5000",
'header' : "G92 X0 Y0 Z0|G90",
'footer' : "G28 X|M84"
}

def cnv(x):
  """ Conversion to external units, based on specification
      of internal units (METRIC or INCH) and command line parameter"""
  if inunit==options.unit or options.unit=="":
    return x
  else:
    if inunit == "mm" and options.unit=="in":
      return x / 25.4
    elif inunit == "in" and options.unit=="mm":
      return x * 25.4
    else:
      return x

def getval(x):
  if "." in x:
    return cnv(float(x))
  else:
    if zero == "lz":
      xx=x+"000000"
      return cnv(float(xx[0:6])/divider)
    else:
      return cnv(float(x)/divider)
    
def parse_config(file):
  with open(file) as c: 
    for cn in c:
      c=cn.strip('\r\n ')
      k = c.split(":")
      if len(k) == 2:
	defaults[k[0]]=k[1]
  


# read configuration files in home directory and current directory

home=os.path.expanduser("~")
if os.path.isfile(home+os.sep+'.exc2gcode'):
  parse_config(home+os.sep+'.exc2gcode')
if os.path.isfile('exc2gcode'):
  parse_config('exc2gcode')

# Parse command line arguments

usage = "Usage: %prog [options] <filename>"
cmdline = OptionParser(usage=usage)

cmdline.add_option("-f", "--file",   action="store", type="string", dest="output_file",   default="",   help="Name of output file; if not specified stdout is used")
cmdline.add_option("-u", "--unit",   action="store", type="string", dest="unit",   default=defaults['unit'],   help="Output unit (mm or in); if not specified the unit used in input file is preserved")
cmdline.add_option("-x", "--maxsize",   action="store", type="float", dest="maxsize",   default=float(defaults['maxsize']),   help="Maximum drill diameter (mm or in)")
cmdline.add_option("", "--header",   action="store", type="string", dest="gheader",   default=defaults['header'],   help="Program header")
cmdline.add_option("", "--footer",   action="store", type="string", dest="gfooter",   default=defaults['footer'],   help="Program footer")
cmdline.add_option("", "--spindle-on",   action="store", type="string", dest="spindle_on",   default=defaults['spindle-on'],   help="Spindle ON Command")
cmdline.add_option("", "--spindle-off",   action="store", type="string", dest="spindle_off",   default=defaults['spindle-off'],   help="Spindle OFF Command")
cmdline.add_option("", "--init-cmd",   action="store", type="string", dest="init_cmd",   default=defaults['init-cmd'],   help="Additional initializatiom")
cmdline.add_option("", "--tool-cmd",   action="store", type="string", dest="tool_cmd",   default=defaults['tool-cmd'],   help="Tool Change Command")
cmdline.add_option("", "--msg-cmd",   action="store", type="string", dest="msg_cmd",   default=defaults['msg-cmd'],   help="Display Message Command")
cmdline.add_option("", "--drill-height",   action="store", type="float", dest="drill_height",   default=float(defaults['drill-height']),   help="Drill Height (mm or in)")
cmdline.add_option("", "--safe-height",   action="store", type="float", dest="safe_height",   default=float(defaults['safe-height']),   help="Safe Height  (mm or in)")
cmdline.add_option("", "--tool-change-height",   action="store", type="float", dest="tool_height",   default=float(defaults['tool-change-height']),   help="Tool Change Height  (mm or in)")
cmdline.add_option("", "--drill-speed",   action="store", type="int", dest="drill_speed",   default=int(defaults['drill-speed']),   help="Drill speed (mm/min)")
cmdline.add_option("", "--retract-speed",   action="store", type="int", dest="retract_speed",   default=int(defaults['retract-speed']),   help="Retract speed (mm/min)")
cmdline.add_option("", "--move-speed",   action="store", type="int", dest="move_speed",   default=int(defaults['move-speed']),   help="Move speed (mm/min)")

(options, filenames) = cmdline.parse_args()

# Some sanity checks

if len(filenames) != 1 or options.unit not in ["", "mm", "in"]:
  cmdline.print_help()
  sys.exit(2)

# Let's go

tools = {}     # list of all used tools
zero="lz"      # zero padding mode
inunit="mm"    # internal file unit (comes from METRIC or INCH commands)
unit="mm"      # output unit

of = open(options.output_file, "w") if options.output_file != "" else sys.stdout

mode="none"
with open(filenames[0]) as f: 
  for ln in f:
    l=ln.strip('\r\n ')

    # Wait for program start
    if mode == "none":
      if l == "M48":
        mode = "header"
        of.write(options.gheader.replace("|","\n")+"\n");

    # In header, parse only important commands
    elif mode == "header":
      if l == "%" or l == "M95":   # end of header
        mode = "body"
	sx="0"
	sy="0"
	unit=options.unit if options.unit != "" else inunit
        if unit == "mm":
          of.write("G21\n")
        else:
          of.write("G20\n")
        if options.init_cmd != "":
          of.write(options.init_cmd.replace("|","\n")+"\n")
	of.write("\n")
	for t,d in tools.iteritems():
          of.write("; Tool %02d diameter: %f%s\n" % (t, d, unit))
      else:
        if l[0] == 'T':   # tool diameter specification
	  m=re.search('T([0-9]*)C([0-9.]*).*', l)
	  if m != None and m.group(2) != "":
	    tools[int(m.group(1))] = cnv(float(m.group(2)))
	else:             # Other commands: METRIC and INCH are processed
	  cmd = l.split(",")
	  if cmd[0] == "METRIC":
	    inunit="mm"
            divider=1000
	    for c in cmd[1:]:
	      if c == "TZ":
	        zero="tz"
	      if c == "LZ":
	        zero="lz"
	      if c == "000.000":
	        zerolen = 6
	        divider=1000
	      if c == "000.00":
	        zerolen = 5
	        divider=100
	      if c == "0000.00":
	        zerolen = 6
	        divider=100
	  if cmd[0] == "INCH":
	    inunit="in"
            divider=10000
	    zerolen = 6
	    for c in cmd[1:]:
	      if c == "TZ":
	        zero="tz"
	      if c == "LZ":
	        zero="lz"
	  
    elif mode == "body":
      if l == "M30" or l == "M00":  # End of program
	break
      elif l[0] == 'T':             # Tool change
	m=re.search('T([0-9]*)', l)
	if m != None:
	  # Set of commands for tool change 
          of.write("\n")
          of.write(options.spindle_off.replace("|","\n")+"\n")
          of.write("G00 Z%.3f F%d\n" % (options.tool_height, options.retract_speed))
          of.write("%s Change Drill: %.2f%s\n" % (options.msg_cmd.replace("|","\n"), tools[int(m.group(1))], unit))
          if options.tool_cmd != "":
	    of.write(options.tool_cmd.replace("|","\n")+"\n")
          of.write(options.spindle_on.replace("|","\n")+"\n")
          of.write("G00 Z%.3f F%d\n" % (options.safe_height, options.retract_speed))
          of.write("\n")
      else:                        # Various format of coordinates: XY, X or Y
        m=re.search('X([0-9.]*)Y([0-9.]*)', l)
	if m != None:
	  sx = m.group(1)
	  sy = m.group(2)
	else:
	  m=re.search('X([0-9.]*)', l)
	  if m != None:
	    sx = m.group(1)
	  else:
	    m=re.search('Y([0-9.]*)', l)
	    if m != None:
	      sy = m.group(1)
	# Write set of drill commands 
        of.write("G04 P0\n")
        of.write("G00 X%.3f Y%.3f F%d\n" % (getval(sx), getval(sy), options.move_speed))
        of.write("G01 Z%.3f F%d\n" % (options.drill_height, options.drill_speed))
        of.write("G01 Z%.3f F%d\n" % (options.safe_height, options.retract_speed))

of.write("\n"+options.spindle_off.replace("|","\n")+"\n")
of.write(options.gfooter.replace("|","\n")+"\n");

of.close()

sys.exit(0)

