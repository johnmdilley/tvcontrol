#!/usr/bin/python

import subprocess
import threading
import time
import sys
import socket

class Operation(threading.Thread):
    def __init__(self, operation):
        self.operation = operation
        super(Operation, self).__init__()

    def run(self):
        self.operation()

class TVOperator(object):
    PVR_IP = "192.168.128.101"
    HD_MAP = {
        1: 101,
        2: 102,
        3: 103,
        4: 104,
        5: 105,
        121: 124
    }

    def __init__(self, debug=False):
        self.lock = threading.RLock()
        self.debug=debug

    def ir_send(self, device, operation, count=5):
        with self.lock:
            cmd = "irsend --count=%d SEND_ONCE %s %s" % (count, device, operation)
            print "Running %s" % cmd
            if self.debug:
                print "(Debug)"
            else:
                subprocess.check_output(cmd, shell=True)

    def do_tv_off(self):
        self.ir_send("tv", "POWER_OFF", 10)

    def do_pvr_power(self):
        self.ir_send("pvr", "POWER", 10)

    def do_pvr_off(self):
        if self.get_pvr_power():
            self.ir_send("pvr", "POWER")

    def do_bd_off(self):
        self.ir_send("bd", "POWER_OFF")

    def do_amp_off(self):
        time.sleep(0.5)
        self.ir_send("amp", "POWER_OFF")

    def all_off(self):
        ops = [
            lambda: self.do_tv_off(),
            lambda: self.do_pvr_off(),
            lambda: self.do_bd_off(),
            lambda: self.do_amp_off(),
            ]
        self.run_ops(ops)
    
    def run_ops(self, operations):
        threads = [Operation(x) for x in operations]
        for t in threads:
            t.start()

    def watch_channel(self, channel):
        ops = [
            lambda: self.do_tv_on(),
            lambda: self.do_pvr_watch(channel),
            lambda: self.do_amp_on("PVR"),
            ]

        self.run_ops(ops)
    
    def watch_tv(self):
        ops = [
            lambda: self.do_tv_on(),
            lambda: self.do_pvr_on(),
            lambda: self.do_amp_on("PVR"),
            ]

        self.run_ops(ops)
    
    def watch_bd(self):
        ops = [
            lambda: self.do_tv_on(),
            lambda: self.do_bd_on(),
            lambda: self.do_amp_on("BD"),
            ]

        self.run_ops(ops)
    
    def watch_fire(self):
        ops = [
            lambda: self.do_tv_on(),
            lambda: self.do_amp_on("FIRE"),
            ]

        self.run_ops(ops)
    
    def do_bd_on(self):
        self.ir_send("bd", "POWER_ON")

    def do_tv_on(self):
        self.ir_send("tv", "POWER_ON", 10)
        time.sleep(30)
        self.ir_send("tv2", "HDMI_1")

    def do_pvr_on(self):
        if not self.get_pvr_power():
            self.ir_send("pvr", "POWER")

    def do_pvr_watch(self, channel):
        if not self.get_pvr_power():
            self.ir_send("pvr", "POWER")
            time.sleep(2)

        if channel in self.HD_MAP:
            channel = self.HD_MAP[channel]

        for i in [1000, 100, 10, 1]:
            self.ir_send("pvr", str(channel/i % 10))
            time.sleep(0.5)

    def do_amp_on(self, source):
        if source == "BD":
            device="amp2"
        else:
            device = "amp"

        self.ir_send(device, "SOURCE_%s" % source)
    
    def get_pvr_power(self):
        try:
            socket.create_connection((self.PVR_IP, 9000), 1)
        except:
            return False
        else:
            return True

if __name__ == "__main__":
    operator = TVOperator(debug=True)
    if sys.argv[1] == "off":
        operator.all_off()
    elif sys.argv[1] == "bd":
        operator.watch_bd()
    elif sys.argv[1] == "test":
        operator.do_tv_on()
    else:
        operator.watch_tv(101)
