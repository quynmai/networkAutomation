from netmiko import ConnectHandler
from netmiko import Netmiko
import re
import time

'''
    This program is designed to change the image on a stack of Cisco switches.
    
    pod 816/368
'''

ip_add = input('Enter IP address of device: ')
user_name = input('Enter Username: ')
password = input('Enter password: ')
secret_pass = input('Enter secret password: ')
new_image = input('Enter the image: ')

ios1 = {
    'device_type': 'cisco_xe',
    'ip': ip_add,
    'username': user_name,
    'password': password,
    'secret':secret_pass
}

net_connect = Netmiko(**ios1)
net_connect.enable()

output = net_connect.send_command('dir ?')

stack_flash = re.findall('flash-.:', output)
print(stack_flash)

# modify so that copies to flash-1 and then copies from flash to flash
for stack in stack_flash:
    print('Copying {} on {}'.format(new_image, stack))
    output = net_connect.send_command('copy ftp://calo:calo@10.122.153.158/{} {}'.format(new_image, stack),
                                      expect_string=r'Destination filename')
    output += net_connect.send_command('\n', expect_string=r'#', delay_factor=12)
    print(output)

    output = net_connect.send_command('dir ' + stack)
    print(output)

    file = []
    file = re.findall(new_image, output)

    if new_image not in file:
        print('File not found in', stack)
    else:
        print('File Successfully Downloaded on', stack)


cmd_list = ['no boot system',
            'boot system flash:{}'.format(new_image),
            'exit',
            'wr',
            'show boot system'
            ]

output = net_connect.send_config_set(cmd_list)
print(output)

# Image Change
try:
    output = net_connect.send_command('reload', expect_string=r'[confirm]')
    output+= net_connect.send_command('y', expect_string=r'reloading')
    print('-----------output1--------')
    print(output)
except (EOFError):
    print('Device Reloading - Connection Closed')
    print(output)
net_connect.disconnect()

time.sleep(700)

net_connect = Netmiko(**ios1)
net_connect.enable()

output = net_connect.send_command('show switch')
output += net_connect.send_command('show ver | i image')
print(output)

net_connect.disconnect()

# RETURN