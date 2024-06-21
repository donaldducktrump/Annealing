import time
import qcodes as qc
import numpy as np
from zhinst.qcodes import ZISession

setup_file = __file__
tags = ["Device", "condition", "annealing"]
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
MFLI_lockin.sigins[IN_CHANNEL].autorange(0) #on=1
MFLI_lockin.sigins[IN_CHANNEL].range(1e-2) #on=1
MFLI_lockin.sigins[IN_CHANNEL].scaling(1) #on=1

## current channel setup
MFLI_lockin.currins[IN_CHANNEL].float(0)
MFLI_lockin.currins[IN_CHANNEL].autorange(0)
MFLI_lockin.currins[IN_CHANNEL].range(10e-6)
MFLI_lockin.currins[IN_CHANNEL].scaling(1)

## demodulation setup
MFLI_lockin.demods[DEMOD_INDEX].order(3)
MFLI_lockin.demods[DEMOD_INDEX].sinc(1)
MFLI_lockin.demods[DEMOD_INDEX].enable(1)
MFLI_lockin.demods[DEMOD_INDEX].adcselect(IN_CHANNEL+1)
MFLI_lockin.demods[DEMOD_INDEX].rate(1674)

# # Specify the number of sweeps to perform back-to-back.
# LOOPCOUNT = 1

# sweeper = session.modules.sweeper
# sweeper.device(MFLI_lockin)

# sweeper.gridnode(MFLI_lockin.oscs[OSC_INDEX].freq)
# sweeper.start(1)
# sweeper.stop(500) # 500e3 for MF devices, 50e6 for others
# sweeper.samplecount(500)
# sweeper.xmapping(1)
# sweeper.bandwidthcontrol(2)
# sweeper.bandwidthoverlap(0)
# sweeper.scan(0)
# sweeper.loopcount(LOOPCOUNT)
# sweeper.settling.time(0)
# sweeper.settling.inaccuracy(0.001)
# sweeper.averaging.tc(10)
# sweeper.averaging.sample(10)

class MFLI:
    def __init__(self, 
                 server_host: str,
                 device_id: str):
        self.server_host = server_host
        self.device_id = device_id
        self.session = ZISession(self.server_host)
        print(f"Created an API session to {self.server_host}")
        self.device = self.session.connect_device(self.device_id)
        print(f"connected to {self.device_id}")

    def aquire(self,
               num_shot:int,
               shot_duration:int,
               sampling_rate:int,
               ) -> np.ndarray:
        
        self.device.demods[0].enable(True)

        signals = [
            self.device.demods[0].sample.zi_node.lower() + ".x",
            self.device.demods[0].sample.zi_node.lower() + ".y"
        ]

        total_duration = int(shot_duration*num_shot)
        samples_per_shot = int(np.ceil(sampling_rate*shot_duration)) # number of samples in a singlshot

        daq_module = self.session.modules.daq
        daq_module.device(self.device)
        daq_module.type(0) # continuous acquisition
        daq_module.grid.mode(2)
        """
        grid mode: 
        1 = "nearest": Use the closest data point (nearest neighbour interpolation).
        2 = "linear": Use linear interpolation.
        4: Do not resample the data from the subscribed signal path(s) with the
            highest sampling rate; the horizontal axis data points are determined from
            the sampling rate and the value of grid/cols. Subscribed signals with a
            lower sampling rate are upsampled onto this grid using linear interpolation.
        """
        daq_module.count(num_shot)
        daq_module.duration(shot_duration)
        daq_module.grid.cols(samples_per_shot)

        for signal in signals:
            daq_module.subscribe(signal)

        daq_module.execute()
        clockbase = self.device.clockbase()
        time.sleep(1.5*total_duration)
        

        daq_data = daq_module.read(raw=False, clk_rate=clockbase)
        """
        return ndarray(2, num_shot, samples_per_shot)
        """
        return np.array([
                        [daq_data[signals[0]][i].value[0] for i in range(num_shot)],
                        [daq_data[signals[1]][i].value[0] for i in range(num_shot)]
                        ])
    
    def voltage_setup(self) -> None:
        self.device.demods[0].adcselect(0)
        self.device.demods[0].sinc(1)
        self.device.sigins[0].diff(1)
        return None
    
    def measure_voltage(self,
                        num_shot:int,
                        shot_duration:int,
                        sampling_rate:int,
                        ) -> np.ndarray:
        self.voltage_setup()
        self.device.sigouts[0].on(1)
        v = self.aquire(num_shot, shot_duration, sampling_rate)
        self.device.sigouts[0].on(0)
        return v
    
    def current_setup(self) -> None:
        self.device.demods[0].adcselect(1)
        self.device.demods[0].sinc(1)
        self.device.sigins[0].diff(0)
        return None
    
    def measure_current(self,
                        num_shot:int,
                        shot_duration:int,
                        sampling_rate:int,
                        ) -> np.ndarray:
        self.current_setup()
        self.device.sigouts[0].on(1)
        i = self.aquire(num_shot, shot_duration, sampling_rate)
        self.device.sigouts[0].on(0)
        return i
    
    def measure_impedance(self,
                        num_shot:int,
                        shot_duration:int,
                        sampling_rate:int,
                        ) -> np.ndarray:
        v_array = self.measure_voltage(num_shot, shot_duration, sampling_rate)
        i_array = self.measure_current(num_shot, shot_duration, sampling_rate)
        v_phasor = v_array[0] + 1j*v_array[1]
        i_phasor = i_array[0] + 1j*i_array[1]
        return v_phasor/i_phasor
