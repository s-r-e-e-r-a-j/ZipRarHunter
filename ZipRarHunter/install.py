import os
import sys

if os.geteuid() != 0:
    print("please run as root or with sudo")
    sys.exit(1)
choice = input('[+] to install press (Y) to uninstall press (N) >> ')
run = os.system
if str(choice) =='Y' or str(choice)=='y':

    run('chmod 755 ZipRarHunter.py')
    run('mkdir /usr/share/ziprarhunter')
    run('cp ZipRarHunter.py /usr/share/ziprarhunter/ZipRarHunter.py')

    cmnd=(' #! /bin/sh \n exec python3 /usr/share/ziprarhunter/ZipRarHunter.py "$@"')
    with open('/usr/bin/ziprarhunter','w')as file:
        file.write(cmnd)
    run('chmod +x /usr/bin/ziprarhunter & chmod +x /usr/share/ziprarhunter/ZipRarHunter.py')
    print('''\n\ncongratulation ziprarhunter is installed successfully \nfrom now just type \x1b[6;30;42mziprarhunter\x1b[0m in terminal ''')
if str(choice)=='N' or str(choice)=='n':
    run('rm -r /usr/share/ziprarhunter ')
    run('rm /usr/bin/ziprarhunter ')
    print('[!] now ziprarhunter  has been removed successfully')
