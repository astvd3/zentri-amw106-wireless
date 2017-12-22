import requests
import socket

url = 'http://10.10.10.1/command/'

class Netcat:

    """ Python 'netcat like' module """

    def __init__(self, ip, port):

        self.buff = ""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))

    def read(self, length = 1024):

        """ Read 1024 bytes off the socket """

        return self.socket.recv(length)
 
    def read_until(self, data):

        """ Read data into the buffer until we have data """

        while not data in self.buff:
            self.buff += self.socket.recv(1024)
 
        pos = self.buff.find(data)
        rval = self.buff[:pos + len(data)]
        self.buff = self.buff[pos + len(data):]
 
        return rval
 
    def write(self, data):

        self.socket.send(data)
    
    def close(self):

        self.socket.close()
        
def do_web_setup(ip,port,ssid,passkey):
    timeout_count=0;
    while True:
        try:
            response = requests.get(url+'set wlan.ssid '+ssid,timeout=5)
        except requests.exceptions.ConnectTimeout:
            timeout_count+=1
            if timeout_count>=4:
                print('Something Wrong with the connection. Disconnect the device and try again')
                exit()
        except requests.exceptions.ConnectionError:
            time.sleep(1)
            timeout_count+=1
            if timeout_count>=4:
                print('Something Wrong with the connection. Disconnect the device and try again')
                exit()
        else:
            data=response.json()
            if data['response']=='Set OK\r\n':
                print('Network ID Successfully Added')
            else:
                print('Error Adding the Network ID')
            timeout_count=0
            break

            
    while True:
        try:
            if not passkey:
                response = requests.get(url+'set wlan.passkey ""'+passkey,timeout=5)
            else:
                response = requests.get(url+'set wlan.passkey '+passkey,timeout=5)     
        except requests.exceptions.ConnectTimeout:
            timeout_count+=1
            if timeout_count>=4:
                print('Something Wrong with the connection. Disconnect the device and try again')
                exit()
        else:
            data=response.json()
            if data['response']=='Set OK\r\n':
                print('Password Successfully Added')
            else:
                print('Error Adding the Password')
                exit()
            timeout_count=0
            break
            
    while True:
        try:
            response = requests.get(url+'save',timeout=5)
        except requests.exceptions.ConnectTimeout:
            timeout_count+=1
            if timeout_count>=4:
                print('Something Wrong with the connection. Disconnect the device and try again')
        else:
            data=response.json()
            print(data['response'])
            timeout_count=0
            break
            
    while True:
        try:
            response = requests.get(url+'reboot',timeout=5)
        except requests.exceptions.ConnectTimeout:
            timeout_count+=1
            if timeout_count>=4:
                print('Device connected. If connection is not established, re-run this script')
        else:
            data=response.json()
            print(data['response'])
            timeout_count=0
            break
    print('You have successfully connected to your home network!')
    


def do_remote_terminal_setup(ip,port,ssid,passkey):  
    nc = Netcat(ip, port)
    nc.write('get wlan.mac'+'\n')
    result=nc.read(1024)
    nc.write('set wlan.ssid '+ssid+'\n')
    result=nc.read(1024)
    if 'Set OK' in result:
        print('Successfully added Wifi-SSID')
    else:
        print('Failed to set Wifi-SSID')
    if not passkey:
        nc.write('set wlan.passkey ""'+passkey+'\n')
        result=nc.read(1024)
    else:
        nc.write('set wlan.passkey '+passkey+'\n')
        result=nc.read(1024)
    if 'Set OK' in result:
        print('Successfully added Wifi-passkey')
    else:
        print('Failed to set Wifi-passkey')
    nc.write('wlan_scan -v'+'\n')
    result=nc.read(2048)    
    seprated_dump=result.split('\r\n')
    imp_dump=''
    for i in range(0,len(seprated_dump)):
        if ssid in seprated_dump[i]:
            imp_dump=seprated_dump[i]
            break
    if not passkey:
        nc.write('network_verify wifi '+ssid+' '+imp_dump[13:30]+' '+imp_dump[6]+'\n')
        result=nc.read(1024)
        print(result)
        if 'Success' not in result:
            print('Wrong Network Credentials!...Exiting')
            nc.close()
            exit()
    else:
        pass
        #nc.write('network_verify wifi '+ssid+' '+imp_dump[13:30]+' '+imp_dump[6]+' '+imp_dump[37:45]+''++'\n')
    
    nc.write('save'+'\n')
    result=nc.read(1024)
    if 'Success' in result:
        print('Successfully saved the configuration')
    else:
        print('Failed to save configuration')
    nc.write('reboot'+'\n')
    result=nc.read(1024)
    print(result)
    print('Rebooting Now.....')
    nc.close()