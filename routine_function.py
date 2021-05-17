from driver.ControlByWeb.relay import relay
from runtime.data_src_aio import aio

"""
Routines are tasks to be performed at certain time point
"""

# instantiate relay
relay = relay("192.168.0.6")


def relay_routine_frag():
    relay.on(3)
    relay.off(4)


def relay_routine_air():
    relay.off(3)
    relay.on(4)


def aio_routine_frag():
    #aio.fragFlow()
    aio.valveSet(index=3, state=1)

def aio_routine_air():
    #aio.airFlow()
    aio.valveSet(index=3, state=0)


def hello():
    print("Hello, world!")


if __name__ == '__main__':
    aio_routine_air()