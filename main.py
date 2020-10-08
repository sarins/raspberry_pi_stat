import os
import psutil
import time

import board
import digitalio
import adafruit_character_lcd.character_lcd as character_lcd

#Init LCD
lcd_rs = digitalio.DigitalInOut(board.D14)
lcd_en = digitalio.DigitalInOut(board.D15)
lcd_d4 = digitalio.DigitalInOut(board.D17)
lcd_d5 = digitalio.DigitalInOut(board.D18)
lcd_d6 = digitalio.DigitalInOut(board.D27)
lcd_d7 = digitalio.DigitalInOut(board.D22)
lcd_backlight = digitalio.DigitalInOut(board.D13)

lcd_columns = 16
lcd_rows = 2

lcd = character_lcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows, lcd_backlight)

def lcd_msg(l1, l2):
    lcd.message = l1 + "\n" + l2

def lcd_rmsg(l1, l2):
    

#TITLE
uname = os.uname()
nodename = uname.nodename if (len(uname.nodename) < 6) else uname.nodename[:6]
TITLE = nodename + ": {: <8s}"
#CPU
CPU_TITLE = TITLE.format("CPU STAT")
#"Freq[{}]:{: >5s}Ghz".format("L", "{:.1f}".format(2200/1000))
CPU_F = "Freq[{}]:{: >5s}Ghz"
#"Cores[{}]:{: >7s}".format("P", "{:d}".format(1))
CPU_C = "Cores:{: >10s}"
#"Load:{: >11s}".format("{:.2f}%".format(99.3))
CPU_L = "Load:{: >11s}"

#lcd.display = False
#time.sleep(2)
#lcd.backlight = True
#print("truned of back ligth")
#time.sleep(5)
#lcd.backlight = False
#time.sleep(5)

while True:
    lcd.backlight = True
    
    NET_TITLE = TITLE.format("NET STAT")
    NET_L_FIELD = "NET:{:>12s}"
    NET_ADDR_FIELD = "ADDR:{:>11s}"
    net_addrs = psutil.net_if_addrs()
    for nname in net_addrs:
        if nname == "lo":
            continue
        lcd.home()
        #print(NET_L_FIELD.format(nname))
        lcd_msg(NET_TITLE, NET_L_FIELD.format(nname))
        time.sleep(2.0)
        for addr in net_addrs[nname]:
            addr_msg = NET_ADDR_FIELD.format(addr.address)
            print(addr_msg)
            lcd_msg(NET_TITLE, addr_msg)
            time.sleep(2.0)
            if (len(addr_msg) > 16):
                for i in range(len(addr_msg) - 16):
                    lcd.move_left()
                    time.sleep(0.35)
            #print(NET_ADDR_FIELD.format(addr.address))
    
    #---------------
    lcd.home()
    lcd_msg(CPU_TITLE, CPU_F.format("C", str(psutil.cpu_freq().current / 1000)))
    time.sleep(2.0)
    lcd_msg(CPU_TITLE, CPU_F.format("L", str(psutil.cpu_freq().min / 1000)))
    time.sleep(2.0)
    lcd_msg(CPU_TITLE, CPU_F.format("H", str(psutil.cpu_freq().max / 1000)))
    time.sleep(2.0)
    lcd_msg(CPU_TITLE, CPU_C.format(str(psutil.cpu_count(logical=False)) + "/" + str(psutil.cpu_count())))
    time.sleep(2.0)
    lcd_msg(CPU_TITLE, CPU_L.format("{:.2f}%".format(psutil.cpu_percent(interval=None))))
    time.sleep(2.0)

    #print(CPU_TITLE)
    #print(CPU_F.format("C", str(psutil.cpu_freq().current / 1000)))
    #print(CPU_F.format("L", str(psutil.cpu_freq().min / 1000)))
    #print(CPU_F.format("H", str(psutil.cpu_freq().max / 1000)))
    #print(CPU_C.format(str(psutil.cpu_count(logical=False)) + "/" + str(psutil.cpu_count())))
    #print(CPU_L.format("{:.2f}%".format(psutil.cpu_percent(interval=None))))

    #MEM
    VM_TITLE = TITLE.format("VM STAT")
    SM_TITLE = TITLE.format("SM STAT")
    #("{}:{:>" + str(15 - len("total")) + "s}").format("total".capitalize(), "11g")
    MEM_F_PREFIX = "{}:{:>"
    MEM_F_SUFFIX = "s}"
    #print(MEM_TITLE)
    vm = psutil.virtual_memory()
    for n in vm._fields:
        if (n == 'percent'):
            #print((MEM_F_PREFIX + str(14 - len(n)) + "s}%").format(n.capitalize(), str(getattr(vm, n))))
            lcd_msg(VM_TITLE, (MEM_F_PREFIX + str(14 - len(n)) + "s}%").format(n.capitalize(), str(getattr(vm, n))))
        else:
            #print((MEM_F_PREFIX + str(15 - len(n)) + MEM_F_SUFFIX).format(n.capitalize(), psutil._common.bytes2human(getattr(vm, n))))
            lcd_msg(VM_TITLE, (MEM_F_PREFIX + str(15 - len(n)) + MEM_F_SUFFIX).format(n.capitalize(), psutil._common.bytes2human(getattr(vm, n))))
        time.sleep(2.0)
    sm = psutil.swap_memory()
    for n in sm._fields:
        if (n == 'percent'):
            #print((MEM_F_PREFIX + str(14 - len(n)) + "s}%").format(n.capitalize(), str(getattr(sm, n))))
            lcd_msg(SM_TITLE, (MEM_F_PREFIX + str(14 - len(n)) + "s}%").format(n.capitalize(), str(getattr(sm, n))))
        else:
            #print((MEM_F_PREFIX + str(15 - len(n)) + MEM_F_SUFFIX).format(n.capitalize(), psutil._common.bytes2human(getattr(sm, n))))
            lcd_msg(SM_TITLE, (MEM_F_PREFIX + str(15 - len(n)) + MEM_F_SUFFIX).format(n.capitalize(), psutil._common.bytes2human(getattr(sm, n))))
        time.sleep(2.0)

    #FS
    FS_TITLE = TITLE.format("FS STAT")
    FS_PI_FIELD = "D:{:>6s}|T:{:>5s}"
    FS_PU_FIELD = "A:{:>6s}|U:{:>5s}"
    #print(FS_TITLE)
    for p in psutil.disk_partitions(all=False):
        dev = p.device.replace("/dev/", "")
        ld = len(dev)
        dev = dev if (ld < 6) else "*" + dev[ld - 5:ld]
        lt = len(p.fstype)
        fst = p.fstype if (lt < 5) else "*" + p.fstype[lt - 4:lt]
        #print(FS_PI_FIELD.format(dev, fst))
        lcd_msg(FS_TITLE, FS_PI_FIELD.format(dev, fst))
        time.sleep(2.0)
        usage = psutil.disk_usage(p.mountpoint)
        #print(FS_PU_FIELD.format(psutil._common.bytes2human(usage.total), "{:.0f}%".format(usage.percent)))
        lcd_msg(FS_TITLE, FS_PU_FIELD.format(psutil._common.bytes2human(usage.total), "{:.0f}%".format(usage.percent)))
        time.sleep(2.0)

    #I/O counter
    IO_TITLE = TITLE.format("IO STAT")
    IO_L_FIELD = "DISK:{:>11s}"
    IO_CI_FIELD = "I:{:>6s}|S{:>6s}"
    IO_CO_FIELD = "O:{:>6s}|S{:>6s}"
    #print(IO_TITLE)
    ioc = psutil.disk_io_counters(perdisk=True)
    for c in ioc:
        #print(IO_L_FIELD.format(c))
        lcd_msg(IO_TITLE, IO_L_FIELD.format(c))
        time.sleep(2.0)
        #print(IO_CI_FIELD.format(psutil._common.bytes2human(ioc[c].read_bytes), psutil._common.bytes2human(ioc[c].read_time / 1000).replace(".0B", "")))
        lcd_msg(IO_TITLE, IO_CI_FIELD.format(psutil._common.bytes2human(ioc[c].read_bytes), psutil._common.bytes2human(ioc[c].read_time / 1000).replace(".0B", "")))
        time.sleep(2.0)
        #print(IO_CO_FIELD.format(psutil._common.bytes2human(ioc[c].write_bytes), psutil._common.bytes2human(ioc[c].write_time / 1000).replace(".0B", "")))
        lcd_msg(IO_TITLE, IO_CO_FIELD.format(psutil._common.bytes2human(ioc[c].write_bytes), psutil._common.bytes2human(ioc[c].write_time / 1000).replace(".0B", "")))
        time.sleep(2.0)
    
    lcd.backlight = False
    time.sleep(10)
#Network
