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
    lcd.clear()
    lcd.message = l1 + "\n" + l2
    time.sleep(pause)
    l2_len = len(l2)
    if (l2_len > 16):
        while (l2_len - 16) > 0:
            l2 = l2[1:]
            l2_len = len(l2)
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
VM_TITLE = TITLE.format("Memory")
SM_TITLE = TITLE.format("Swap")
MEM_F_PREFIX = "{}:{:>"
MEM_F_SUFFIX = "s}"
#FS
FS_T_FIELD = "FS type: {:>s}"
FS_PU_FIELD = "Size: {:>s}, Used: {:>s}"
#I/O counter
IO_CI_FIELD = "Input: {:>s}, Elapsed: {:>s}s"
IO_CO_FIELD = "Output: {:>s}, Elapsed: {:>s}s"
# NET
NET_ADDR_FIELD = "Addr: {:>s}"

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
        dev = dev if (ld < 8) else "*" + dev[ld - 7:ld]
        dev_title = TITLE.format(dev)
        lcd_msg(dev_title, FS_T_FIELD.format(p.fstype))
        usage = psutil.disk_usage(p.mountpoint)
        lcd_msg(
            dev_title,
            FS_PU_FIELD.format(psutil._common.bytes2human(usage.total),
                               "{:.0f}%".format(usage.percent)))
    #I/O counter
    ioc = psutil.disk_io_counters(perdisk=True)
    for c in ioc:
        if (c.startswith("ram") | c.startswith("loop")):
            continue
        lc = len(c)
        dev = c if (lc < 8) else "*" + c[lc - 7:lc]
        dev_title = TITLE.format(dev)
        lcd_msg(
            dev_title,
            IO_CI_FIELD.format(
                psutil._common.bytes2human(ioc[c].read_bytes),
                str(ioc[c].read_time / 1000)))
        lcd_msg(
            dev_title,
            IO_CO_FIELD.format(
                psutil._common.bytes2human(ioc[c].write_bytes),
                str(ioc[c].write_time / 1000)))
    #NET
    net_addrs = psutil.net_if_addrs()
    for nname in net_addrs:
        if nname == "lo":
            continue
        ln = len(nname)
        nn = nname if (ln < 8) else "*" + nname[ln - 7:ln]
        nn_title = TITLE.format(nn)
        for addr in net_addrs[nname]:
            addr_msg = NET_ADDR_FIELD.format(addr.address)
            lcd_msg(nn_title, addr_msg)
    # down
    lcd.clear()
    lcd.backlight = False
    time.sleep(10)