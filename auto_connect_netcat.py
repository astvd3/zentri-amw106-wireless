from wifi_lib import *
from connect_lib import *
import sys
from colorama import init
init(strip=not sys.stdout.isatty())
from termcolor import cprint 
from pyfiglet import figlet_format

cprint(figlet_format('Wi-Fi Setup!', font='starwars'),'blue', 'on_white', attrs=['bold']) 
    

scan_and_connect()    
    
while True:
    try:
        ch_number=int(input('Select your home network number :'))
    except ValueError:
        print('Input Channel Number Please!')
    except NameError:
        print('Input Channel Number Please!')
    else:
        break
                
ssid=get_ssid(ch_number)

password=raw_input('Enter Password to your home network :')

try:
    response = requests.get(url+'get wlan.mac',timeout=3)
except requests.exceptions.ConnectTimeout:
    print('Web Setup Not Running. Trying SoftAP remote terminal setup ')
    web_setup=0
    do_remote_terminal_setup('10.10.10.1',2000,ssid,password)
else:
    print('Web Setup Running....')
    web_setup=1
    do_web_setup('10.10.10.1',2000,ssid,password)



