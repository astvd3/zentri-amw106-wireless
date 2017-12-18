from wireless import Wireless
import wifi
import time
import socket
wifilist = []
wireless=Wireless()
interface=wireless.interface()

def Search():
    cells = wifi.Cell.all(interface)

    for cell in cells:
        wifilist.append(cell)

    return wifilist


def FindFromSearchList(ssid):
    wifilist = Search()

    for cell in wifilist:
        if ssid in cell.ssid:
            return cell

    return False


def FindFromSavedList(ssid):
    cell = wifi.Scheme.find(interface, ssid)

    if cell:
        return cell

    return False


def Connect(ssid, password=None):
    cell = FindFromSearchList(ssid)

    if cell:
        savedcell = FindFromSavedList(cell.ssid)

        # Already Saved from Setting
        if savedcell:
            savedcell.activate()
            return cell

        # First time to conenct
        else:
            if cell.encrypted:
                if password:
                    scheme = Add(cell, password)

                    try:
                        scheme.activate()

                    # Wrong Password
                    except wifi.exceptions.ConnectionError:
                        Delete(ssid)
                        return False

                    return cell
                else:
                    return False
            else:
                scheme = Add(cell)

                try:
                    scheme.activate()
                except wifi.exceptions.ConnectionError:
                    Delete(ssid)
                    return False

                return cell
    
    return False


def Add(cell, password=None):
    if not cell:
        return False

    scheme = wifi.Scheme.for_cell(interface, cell.ssid, cell, password)
    scheme.save()
    return scheme


def Delete(ssid):
    if not ssid:
        return False

    cell = FindFromSavedList(ssid)

    if cell:
        cell.delete()
        return True

    return False

def scan_and_connect():
    
    
    wireless.power(False)
    time.sleep(1)
    wireless.power(True)
    time.sleep(1)

    print('Using interface '+interface)
    network=FindFromSearchList('ZentriOS')
    print('\t#'+'Ch. Number'+' \t'+'Wifi Network Name')
    for i in range(0,len(wifilist)):
        print('\t#'+str(i+1)+' \t\t'+wifilist[i].ssid)

    print('Wait for Zentri Device to be connected...')
    try:
        wireless.connect(network.ssid,'password')
    except AttributeError:
        print('Something wrong with the Ethernet Hardware. Try disconnecting all the wifi networks and run the script again')
        exit()
    else:
        print('Zentri Device Connected')
        
def get_ssid(channel_number):
    if channel_number>len(wifilist) or channel_number<0:
        print('Unknown Channel Number : try again')
        exit()
    return wifilist[channel_number-1].ssid