import time
import qcodes as qc
from zhinst.qcodes import ZISession

setup_file = __file__
tags = ["Device", "condition", "probe_or_annealing"]
data_path = "C:/Users/qipe/annealing/data"

wiring = "\n".join([
   "MFLI_lockin-prober",
#    "E8257D_MY51111550 - 1500mm - 10dB - 20dB - In1B",
#    "Out1A - Miteq - 1500mm - N5222A_port2",
#    "N5222A_aux_trig1_out - E8257D_MY51111550_trigger_in",
#    "E8257D_MY51111550_trigger_out - N5222A_meas_trig_in",
])

station = qc.Station()

device_id = "DEV5149"  # 実際のデバイスIDに置き換えてください
server_host = "169.254.254.194"  # 実際のサーバーホストに置き換えてください
session = ZISession(server_host)
MFLI_lockin = session.connect_device(device_id)

#MFLI_lockin = MFLI("DEV5149", host = "169.254.254.194")
station.add_component(MFLI_lockin)

## the config for the output, input, demodulator, internal_oscillator
OUT_CHANNEL = 0
OUT_MIXER_CHANNEL = 1 # UHFLI: 3, HF2LI: 6, MFLI: 1
IN_CHANNEL = 0
DEMOD_INDEX = 0
OSC_INDEX = 0

## setup the lock-in output(bottom row in the gui (left to right))
MFLI_lockin.oscs[OSC_INDEX].freq(11)
MFLI_lockin.demods[OUT_MIXER_CHANNEL].harmonic(1)
MFLI_lockin.demods[OUT_MIXER_CHANNEL].phaseshift(0)
MFLI_lockin.sigouts[OUT_CHANNEL].amplitudes[1].value(2e-3) ## probe: 2e-3
MFLI_lockin.sigouts[OUT_CHANNEL].enables[OUT_MIXER_CHANNEL].value(1)
MFLI_lockin.sigouts[OUT_CHANNEL].imp50(0)
MFLI_lockin.sigouts[OUT_CHANNEL].autorange(0)
MFLI_lockin.sigouts[OUT_CHANNEL].range(10e-3) #10m,100m,1,10
MFLI_lockin.sigouts[OUT_CHANNEL].offset(0)
MFLI_lockin.sigouts[OUT_CHANNEL].diff(0)

MFLI_lockin.sigouts[OUT_CHANNEL].on(False)

## setup the lock-in input(bottom row in the gui (left to right))

## voltage channel setup
MFLI_lockin.sigins[IN_CHANNEL].float(0) #grounded=0
MFLI_lockin.sigins[IN_CHANNEL].diff(1) #diff=1
MFLI_lockin.sigins[IN_CHANNEL].imp50(0) #on=1
MFLI_lockin.sigins[IN_CHANNEL].ac(0) #on=1
# MFLI_lockin.sigins[IN_CHANNEL].autorange(1) #on=1
# MFLI_lockin.sigins[IN_CHANNEL].range(1e-2) #on=1
MFLI_lockin.sigins[IN_CHANNEL].scaling(1) #on=1

## current channel setup
MFLI_lockin.currins[IN_CHANNEL].float(0)
# MFLI_lockin.currins[IN_CHANNEL].autorange(1)
MFLI_lockin.currins[IN_CHANNEL].range(1)
MFLI_lockin.currins[IN_CHANNEL].scaling(1)

# ## demodulation setup
# MFLI_lockin.demods[DEMOD_INDEX].order(3)
# MFLI_lockin.demods[DEMOD_INDEX].sinc(1)
# MFLI_lockin.demods[DEMOD_INDEX].enable(1)
# MFLI_lockin.demods[DEMOD_INDEX].adcselect(IN_CHANNEL)
# MFLI_lockin.demods[DEMOD_INDEX].rate(1674)

# Specify the number of sweeps to perform back-to-back.
LOOPCOUNT = 1

sweeper = session.modules.sweeper
sweeper.device(MFLI_lockin)

sweeper.gridnode(MFLI_lockin.oscs[OSC_INDEX].freq)
sweeper.start(1)
sweeper.stop(500) # 500e3 for MF devices, 50e6 for others
sweeper.samplecount(500)
sweeper.xmapping(1)
sweeper.bandwidthcontrol(2)
sweeper.bandwidthoverlap(0)
sweeper.scan(0)
sweeper.loopcount(LOOPCOUNT)
sweeper.settling.time(0)
sweeper.settling.inaccuracy(0.001)
sweeper.averaging.tc(10)
sweeper.averaging.sample(10)

MFLI_lockin.sigouts[OUT_CHANNEL].on(True)
# MFLI_lockin.sigins[IN_CHANNEL].autorange(1) #on=1
MFLI_lockin.sigins[IN_CHANNEL].autorange(1)
if MFLI_lockin.sigins[IN_CHANNEL].autorange(1, deep=True) != 0:
    # The auto ranging takes some time. We do not want to continue before the
    # best range is found. Therefore, we wait for state to change to 0.
    # These nodes maintain value 1 until autoranging has finished.
    MFLI_lockin.sigins[IN_CHANNEL].autorange.wait_for_state_change(0, timeout=20)
# MFLI_lockin.currins[IN_CHANNEL].autorange(1)
# if MFLI_lockin.sigins[IN_CHANNEL+1].autorange(1, deep=True) != 0:
#     # The auto ranging takes some time. We do not want to continue before the
#     # best range is found. Therefore, we wait for state to change to 0.
#     # These nodes maintain value 1 until autoranging has finished.
#     MFLI_lockin.sigins[IN_CHANNEL+1].autorange.wait_for_state_change(0, timeout=20)
MFLI_lockin.sigouts[OUT_CHANNEL].on(False)