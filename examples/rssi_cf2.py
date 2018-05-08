# cflib can be installed via 'pip install cflib'
import cflib.drivers.crazyradio as crazyradio

cradio = crazyradio.Crazyradio()

# Connection parameter for the CF2
cradio.set_data_rate(cradio.DR_2MPS)
cradio.set_channel(80)

for _ in range(10000):
    pk = cradio.send_packet((0xff, ))
    print len(pk.data)

    # Filter for NULL packet that includes a RSSI measurement
    # -> Null packet have a header of 0xF3, with a mask of 0xF3
    # -> RSSI NULL packets have 1 after the header, and the RSSI after
    if pk.ack and len(pk.data) > 2 and \
       pk.data[0] & 0xf3 == 0xf3 and pk.data[1] == 0x01:
        print("RSSI: -{}dBm".format(pk.data[2]))