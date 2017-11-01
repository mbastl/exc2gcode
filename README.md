# exc2gcode

Tool to convert excellon files to 3D printer compatible g-code

Features:

* creates Repetier compatible g-code from Excellon format
* supports metric or imperial units for both input and output
* rich options enable fine control of drilling process


        Usage: exc2gcode.py [options] <filename>
        
        Options:
        -h, --help            show this help message and exit
        -f OUTPUT_FILE, --file=OUTPUT_FILE
        			Name of output file; if not specified stdout is used
        -u UNIT, --unit=UNIT  Output unit (mm or in); if not specified the unit used
        			in imput file is preserved
        -x MAXSIZE, --maxsize=MAXSIZE
        			Maximum drill diameter (mm or in)
        --header=GHEADER      Program header
        --footer=GFOOTER      Program footer
        --spindle-on=SPINDLE_ON
        			Spindle ON Command
        --spindle-off=SPINDLE_OFF
        			Spindle OFF Command
        --init-cmd=INIT_CMD   Additional initializatiom
        --tool-cmd=TOOL_CMD   Tool Change Command
        --msg-cmd=MSG_CMD     Display Message Command
        --drill-height=DRILL_HEIGHT
        			Drill Height (mm or in)
        --safe-height=SAFE_HEIGHT
        			Safe Height  (mm or in)
        --tool-change-height=TOOL_HEIGHT
        			Tool Change Height  (mm or in)
        --drill-speed=DRILL_SPEED
        			Drill speed (mm/min)
        --retract-speed=RETRACT_SPEED
        			Retract speed (mm/min)
        --move-speed=MOVE_SPEED
        			Move speed (mm/min)

If *Program Header* of *Program Footer* are left empty reasonable and safe defaults are used.

Multiline commands are supported. Vertical bar (|) can be used as command separator` it will be replaced by newline in output file.

Predefined valuse can be stored in configuration files:
* file named `exc2gcode` in current directory
* file named `.exc2gcode` in user's home directory (`~/.exc2gcode` or `%USERPROFILE%\.exc2gcode`, depends on operating system)

First the file in user's home directory is processed, then file in current directory is processed and finally command line arguments are applied. Configuration file
format is straightforward - name of long command line option separated from value by colon, one option per line:

	header:G92 X0 Y0 Z0|G90
	tool-change-height:40
	drill-speed:30
	tool-cmd:M226 P11 S0

