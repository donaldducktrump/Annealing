import os
import time

import numpy as np
from plottr.data.datadict_storage import DataDict, DDH5Writer
from tqdm import tqdm

from setup_annealing import *

measurement_name = os.path.basename(__file__)[:-3]

# sample_nodes = [
#     MFLI_lockin.demods[DEMOD_INDEX].sample.x,
#     MFLI_lockin.demods[DEMOD_INDEX].sample.y
# ]

TOTAL_DURATION = 50  # 秒
SAMPLING_RATE = 100  # サンプル/秒
BURST_DURATION =50  # 秒ffff

num_cols = int(np.ceil(SAMPLING_RATE * BURST_DURATION))
num_bursts = int(np.ceil(TOTAL_DURATION / BURST_DURATION))

daq_module = session.modules.daq
daq_module.device(MFLI_lockin)
daq_module.type(0)  # 継続的な取得
daq_module.grid.mode(2)
daq_module.count(1)
daq_module.duration(BURST_DURATION)
daq_module.preview(True)
daq_module.grid.cols(num_cols)
daq_module.level(0.00000100)
daq_module.endless(0)

prober = MFLI("169.254.254.194", "DEV5149")

# データ保存設定
daq_module.save.fileformat(3)
daq_module.save.filename('zi_toolkit_acq_example')
daq_module.save.saveonread(1)

# daq_module = daq.dataAcquisitionModule()
# daq_module.
# daq_module.set('triggernode', '/dev5149/demods/0/sample.R')
# daq_module.set('preview', 1)
# daq_module.set('MFLI_lockin', 'dev5149')
# daq_module.set('historylength', 100)
# daq_module.set('bandwidth', 0.00000000)
# daq_module.set('hysteresis', 0.01000000)
# daq_module.set('level', 0.10000000)
# daq_module.set('save/directory', 'C:\Users\qipe\Documents\Zurich Instruments\LabOne\WebServer')
# daq_module.set('clearhistory', 1)
# daq_module.set('clearhistory', 1)
# daq_module.set('bandwidth', 0.00000000)

sample_node = MFLI_lockin.demods[0].sample.zi_node.lower() + ".r"

daq_module.subscribe(sample_node)
clockbase = MFLI_lockin.clockbase()

ts0 = np.nan
timeout = 1.5 * TOTAL_DURATION
start_time = time.time()
results = {x: [] for x in sample_node}

# Start recording data
# daq_module.execute()

OUT_CHANNEL = 0

MFLI_lockin.sigouts[OUT_CHANNEL].on(True)
# if MFLI_lockin.sigins[IN_CHANNEL+1].autorange(1, deep=True) != 0:
#     # The auto ranging takes some time. We do not want to continue before the
#     # best range is found. Therefore, we wait for state to change to 0.
#     # These nodes maintain value 1 until autoranging has finished.
#     MFLI_lockin.sigins[IN_CHANNEL+1].autorange.wait_for_state_change(0, timeout=20)

daq_module.execute()
daq_data = daq_module.read(raw=False, clk_rate=clockbase)
progress = daq_module.raw_module.progress()[0]
time.sleep(timeout)
daq_data = daq_module.read(raw=False, clk_rate=clockbase)

MFLI_lockin.sigouts[OUT_CHANNEL].on(False)
daq_module.unsubscribe(sample_node)

# data_dict = DataDict(
#     time=dict(unit="s"),
#     amp=dict(unit="A", axes=["time"])
# )

data_dict = DataDict(
    time=dict(unit="s"),
    resistance=dict(unit="Ohm", axes=["time"])
)

data_dict.validate()

# with DDH5Writer(data_dict, data_path, name=measurement_name) as writer:
#     for power in tqdm(np.linspace(-50, 0, 6)):
#         vna.power(power)
#         vna.run_sweep()
#         writer.add_data(
#             frequency=vna.frequencies(),
#             power=power,
#             s11=vna.trace(),
#         )

time_lst = [] 
resistance = []
length = 0

for num in tqdm(range(4)):
    TOTAL_DURATION = 1  # 秒
    SAMPLING_RATE = 100  # サンプル/秒
    BURST_DURATION =1  # 秒ffff

    num_cols = int(np.ceil(SAMPLING_RATE * BURST_DURATION))
    num_bursts = int(np.ceil(TOTAL_DURATION / BURST_DURATION))

    daq_module = session.modules.daq
    daq_module.device(MFLI_lockin)
    daq_module.type(0)  # 継続的な取得
    daq_module.grid.mode(2)
    daq_module.count(1)
    daq_module.duration(BURST_DURATION)
    daq_module.preview(True)
    daq_module.grid.cols(num_cols)
    daq_module.level(0.00000100)
    daq_module.endless(0)
    ## setup the lock-in output(bottom row in the gui (left to right))
    MFLI_lockin.oscs[OSC_INDEX].freq(500)
    MFLI_lockin.demods[OUT_MIXER_CHANNEL].harmonic(1)
    MFLI_lockin.demods[OUT_MIXER_CHANNEL].phaseshift(0)
    MFLI_lockin.sigouts[OUT_CHANNEL].amplitudes[1].value(0.9) ## probe: 2e-3
    MFLI_lockin.sigouts[OUT_CHANNEL].enables[OUT_MIXER_CHANNEL].value(1)
    MFLI_lockin.sigouts[OUT_CHANNEL].imp50(0)
    MFLI_lockin.sigouts[OUT_CHANNEL].autorange(0)
    MFLI_lockin.sigouts[OUT_CHANNEL].range(1) #10m,100m,1,10
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
    MFLI_lockin.sigins[IN_CHANNEL].range(1) #on=1
    MFLI_lockin.sigins[IN_CHANNEL].scaling(1) #on=1

    ## current channel setup
    MFLI_lockin.currins[IN_CHANNEL].float(0)
    MFLI_lockin.currins[IN_CHANNEL].autorange(0)
    MFLI_lockin.currins[IN_CHANNEL].range(1e-2)
    MFLI_lockin.currins[IN_CHANNEL].scaling(1)

    MFLI_lockin.sigouts[OUT_CHANNEL].on(True)

    # if MFLI_lockin.sigins[IN_CHANNEL+1].autorange(1, deep=True) != 0:
    #     # The auto ranging takes some time. We do not want to continue before the
    #     # best range is found. Therefore, we wait for state to change to 0.
    #     # These nodes maintain value 1 until autoranging has finished.
    #     MFLI_lockin.sigins[IN_CHANNEL+1].autorange.wait_for_state_change(0, timeout=20)

    start_annealing = time.time()

    daq_module.execute()
    daq_data = daq_module.read(raw=False, clk_rate=clockbase)
    progress = daq_module.raw_module.progress()[0]
    time.sleep(timeout)
    daq_data = daq_module.read(raw=False, clk_rate=clockbase)

    MFLI_lockin.sigouts[OUT_CHANNEL].on(False)
    daq_module.unsubscribe(sample_node)
    
    end_annealing=time.time()

    length = end_annealing - start_annealing

    #measure_impedance
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

    Z_array = prober.measure_impedance(10, 0.2, 30e2)
    X_array = Z_array.real
    Y_array = Z_array.imag
    X_ave = np.average(X_array)
    X_std = np.std(X_array)
    Y_ave = np.average(Y_array)
    Y_std = np.std(Y_array)

    R_ave = np.sqrt(X_ave**2 + Y_ave**2)
    R_std = np.abs(X_ave/R_ave)*X_std + np.abs(Y_ave/R_ave)*Y_std
    
    time_lst.append(length)
    resistance.append(R_ave)

with DDH5Writer(data_dict, data_path, name = measurement_name) as writer:
    writer.add_tag(tags)
    writer.backup_file([__file__, setup_file])
    writer.save_text("wiring.md", wiring)
    writer.save_dict("station_snapshot.json", station.snapshot())
    writer.add_data(
            # time = daq_data[sample_node][0][2],
            # amp = daq_data[sample_node][0][1],
            time = time_lst,
            resistance = resistance,
        )