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

lcd = character_lcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6,
                                       lcd_d7, lcd_columns, lcd_rows,
                                       lcd_backlight)


def lcd_msg(l1, l2, pause=2, move_speed=0.4):
    lcd.home()
    lcd.message = l1 + "\n" + l2
    time.sleep(pause)
    l2_len = len(l2)
    if (l2_len > 16):
        while (l2_len - 16) > 0:
            l2 = l2[1:]
            lcd.message = l1 + "\n" + l2
            time.sleep(move_speed)
        time.sleep(pause - move_speed)


#TITLE
uname = os.uname()
nodename = uname.nodename if (len(uname.nodename) < 6) else uname.nodename[:6]
TITLE = nodename + ": {: <8s}"
#CPU
CPU_TITLE = TITLE.format("CPU STAT")
CPU_F = "Freq[{}]:{: >5s}Ghz"
CPU_C = "Cores:{: >10s}"
CPU_L = "Load:{: >11s}"
#MEM
VM_TITLE = TITLE.format("VM STAT")
SM_TITLE = TITLE.format("SM STAT")
MEM_F_PREFIX = "{}:{:>"
MEM_F_SUFFIX = "s}"
#FS
FS_TITLE = TITLE.format("FS STAT")
FS_PI_FIELD = "D:{:>6s}|T:{:>5s}"
FS_PU_FIELD = "A:{:>6s}|U:{:>5s}"
#I/O counter
IO_TITLE = TITLE.format("IO STAT")
IO_L_FIELD = "DISK:{:>11s}"
IO_CI_FIELD = "I:{:>6s}|S{:>6s}"
IO_CO_FIELD = "O:{:>6s}|S{:>6s}"
# NET
NET_TITLE = TITLE.format("NET STAT")
NET_L_FIELD = "NET:{:>12s}"
NET_ADDR_FIELD = "ADDR:{:>11s}"

while True:
    lcd.backlight = True
    #---------------
    lcd_msg(CPU_TITLE, CPU_F.format("C",
                                    str(psutil.cpu_freq().current / 1000)))
    lcd_msg(CPU_TITLE, CPU_F.format("L", str(psutil.cpu_freq().min / 1000)))
    lcd_msg(CPU_TITLE, CPU_F.format("H", str(psutil.cpu_freq().max / 1000)))
    lcd_msg(
        CPU_TITLE,
        CPU_C.format(
            str(psutil.cpu_count(logical=False)) + "/" +
            str(psutil.cpu_count())))
    lcd_msg(CPU_TITLE,
            CPU_L.format("{:.2f}%".format(psutil.cpu_percent(interval=None))))
    # MEM
    vm = psutil.virtual_memory()
    for n in vm._fields:
        if (n == 'percent'):
            lcd_msg(VM_TITLE, (MEM_F_PREFIX + str(14 - len(n)) + "s}%").format(
                n.capitalize(), str(getattr(vm, n))))
        else:
            lcd_msg(VM_TITLE,
                    (MEM_F_PREFIX + str(15 - len(n)) + MEM_F_SUFFIX).format(
                        n.capitalize(),
                        psutil._common.bytes2human(getattr(vm, n))))
    sm = psutil.swap_memory()
    for n in sm._fields:
        if (n == 'percent'):
            lcd_msg(SM_TITLE, (MEM_F_PREFIX + str(14 - len(n)) + "s}%").format(
                n.capitalize(), str(getattr(sm, n))))
        else:
            lcd_msg(SM_TITLE,
                    (MEM_F_PREFIX + str(15 - len(n)) + MEM_F_SUFFIX).format(
                        n.capitalize(),
                        psutil._common.bytes2human(getattr(sm, n))))
    #FS
    for p in psutil.disk_partitions(all=False):
        dev = p.device.replace("/dev/", "")
        ld = len(dev)
        dev = dev if (ld < 6) else "*" + dev[ld - 5:ld]
        lt = len(p.fstype)
        fst = p.fstype if (lt < 5) else "*" + p.fstype[lt - 4:lt]
        lcd_msg(FS_TITLE, FS_PI_FIELD.format(dev, fst))
        usage = psutil.disk_usage(p.mountpoint)
        lcd_msg(
            FS_TITLE,
            FS_PU_FIELD.format(psutil._common.bytes2human(usage.total),
                               "{:.0f}%".format(usage.percent)))
    #I/O counter
    ioc = psutil.disk_io_counters(perdisk=True)
    for c in ioc:
        lcd_msg(IO_TITLE, IO_L_FIELD.format(c))
        lcd_msg(
            IO_TITLE,
            IO_CI_FIELD.format(
                psutil._common.bytes2human(ioc[c].read_bytes),
                psutil._common.bytes2human(ioc[c].read_time / 1000).replace(
                    ".0B", "")))
        lcd_msg(
            IO_TITLE,
            IO_CO_FIELD.format(
                psutil._common.bytes2human(ioc[c].write_bytes),
                psutil._common.bytes2human(ioc[c].write_time / 1000).replace(
                    ".0B", "")))
    #NET
    net_addrs = psutil.net_if_addrs()
    for nname in net_addrs:
        if nname == "lo":
            continue
        lcd_msg(NET_TITLE, NET_L_FIELD.format(nname))
        for addr in net_addrs[nname]:
            addr_msg = NET_ADDR_FIELD.format(addr.address)
            lcd_msg(NET_TITLE, addr_msg)
    # down
    lcd.backlight = False
    time.sleep(10)