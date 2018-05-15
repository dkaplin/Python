import binascii
import struct
import sys

from pyModbusTCP.client import ModbusClient

def IEEE_754(upper, lower):
    # Packs two 16 bit integer numbers into one
    # Once packed the 32 bit value is actually in IEEE-754 format
    # but Python thinks otherwise so it needs translated to a float
    int_value = upper*65536 + lower
    
    # Concert the integer into hex
    hex_value = hex(int_value)
    
    # Now remove the 0x and store the hex value as a string
    hxstr = hex_value[2:len(hex_value)]
    
    # Convert the string to IEEE-754
    s = "".join([binascii.a2b_hex(s) for s in hxstr.split()])
    v = struct.unpack(">f",s)[0]
    
    return v


try:
    c = ModbusClient(host="192.168.1.126", port=502)

except ValueError:
    print "Error with host or port params"
    sys.exit()    
    
# The eGauge meter is set to ID 3   
c.unit_id(3)

# Turn on debug
c.debug(True)

# Try opening the TCP port
c.open()

# Try reading out line voltages
if c.is_open():
    
    # Read out 8 registers at once, this will pull out L1, L2, L1-L2 (L1-L2 is the measured RMS between L1 and L2 which is 240VAC)
    # Referring to the generated register map L1 RMS starts at address 500, L2 at 502 and L1-L2 at 506
    # This will use Modbus function code 4 to read out mulitple input registers
    reg = c.read_input_registers(500,8)
    
    print '\nReturned List:'
    print reg
    c.close()
    
    # So again since this is Modbus each register contains 2 bytes of data.  Keep in mind Modbus could
    # give two shits about the formate of the data IE float, singed, unsinged.  With that said this damn
    # eGuage device slits up a IEEE-754 value into two 16 bit values so we need to combine the two integer
    # value into one and have python interpret that as a IEEE-754 float
    
    # L1 is in location 0 and 1 of the returned list
    l1_rms = IEEE_754(reg[0], reg[1])
    print "\nL1 RMS Voltage: %0.3f VAC" % l1_rms
    
    # L2 RMS voltage is in location 2 and 3 of the returned list
    l2_rms = IEEE_754(reg[2], reg[3])
    print "L2 RMS Voltage: %0.3f VAC" % l2_rms
    
    # RMS voltage between L1 and L2 is location 6 and 7 of the returned list
    l1_l2_rms = IEEE_754(reg[6], reg[7])    
    print "L1-L2 RMS Voltage: %0.3f VAC" % l1_l2_rms
else:
    print "TCP Port Not Open"