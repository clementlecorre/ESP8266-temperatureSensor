import socket
import time
import machine
import dht
import urequests
import onewire, ds18x20
from machine import Timer


# Setting
WIFI_CONNECT_SSID = "******"
WIFI_CONNECT_PASSWORD = "******"
INFLUX_URL = "http://localhost:8086"
INFLUX_DB = "temp"
INFLUX_ID_FOR_DEVICE = "bedroom"
DH11_PIN = 4

def do_flashes(i):
    if i<1:
        i=1
    pin = machine.Pin(2, machine.Pin.OUT)
    for z in range(0,i):
        time.sleep_ms(250)
        pin.value(not pin.value())
        time.sleep_ms(250)
        pin.value(not pin.value())
    pin.value(1)

def do_connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(WIFI_CONNECT_SSID, WIFI_CONNECT_PASSWORD)
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())
    do_flashes(2)

def post_data(data):
    url = INFLUX_URL + "/write?db=" + INFLUX_DB
    data = (INFLUX_ID_FOR_DEVICE + ",tag1=x1,tag2=x2 temperature=%s" % (str(data)))
    resp = urequests.post(url, data=data)

def get_temperature():
    dat = machine.Pin(DS18X20_PIN)
    ds = ds18x20.DS18X20(onewire.OneWire(dat))
    roms = ds.scan()
    print('found devices:', roms)
    if len(roms)>0:
        templist = []
        for i in range(10):
            ds.convert_temp()
            time.sleep_ms(1000)
            temp = ds.read_temp(roms[0])
            templist.append(temp)
        templist.remove(max(templist))
        templist.remove(max(templist))
        templist.remove(min(templist))
        templist.remove(min(templist))
        sum_of_temps = 0
        for temp in templist:
            sum_of_temps = sum_of_temps + temp
        final_temp = sum_of_temps/6
        print('Final temp: ', final_temp)
        return final_temp

def force_reset():
    print("Machine inactive for too long, this is not normal, rebooting!")
    machine.reset()

if machine.reset_cause() == machine.DEEPSLEEP_RESET:
    print('Woke from a deep sleep')

tim = Timer(-1)
tim.init(period=120000, mode=Timer.ONE_SHOT, callback=lambda
t:force_reset())

do_flashes(2)
do_connect()
time.sleep_ms(2000)
data = get_temperature()
print(data)
post_data(data)

print('set RTC alarm to wake up later')
rtc = machine.RTC()
rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
rtc.alarm(rtc.ALARM0, 600000) #  After 600 secondes WakeUp
print('deep sleep in 20 seconds')
time.sleep_ms(15000)
print('deep sleep in 5 seconds')
time.sleep_ms(2000)
print('deep sleep in 3 seconds')
time.sleep_ms(1000)
print('deep sleep in 2 seconds')
time.sleep_ms(2000)
print('deep sleep in 1 seconds')
time.sleep_ms(1000)
print('deep sleep now! waking up in 600 seconds')
machine.deepsleep()
