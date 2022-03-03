import upnpclient

devices = upnpclient.discover()
for device in devices:
    if hasattr(device, 'WANIPConn1'):
        print(device.WANIPConn1.AddPortMapping(
            NewRemoteHost="0.0.0.0",
            NewExternalPort=49152,
            NewProtocol="TCP",
            NewInternalPort=49152,
            NewInternalClient="192.168.1.205",
            NewEnabled='1',
            NewPortMappingDescription="NetAdmin Server Port Forward",
            NewLeaseDuration=100000
        ))