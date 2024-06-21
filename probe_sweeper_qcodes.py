import os
import time
import numpy as np
from plottr.data.datadict_storage import DataDict, DDH5Writer
from tqdm import tqdm
from setup_probe import *

measurement_name = os.path.basename(__file__)[:-3]

# Define parameters
TOTAL_DURATION = 60  # seconds
VOLTAGE_DURATION = 1  # seconds
SAMPLING_RATE = 100  # samples/second
VOLTAGE_LEVEL = 0.9  # Volts

num_cols = int(np.ceil(SAMPLING_RATE * VOLTAGE_DURATION))
num_cycles = int(TOTAL_DURATION / VOLTAGE_DURATION / 2)

daq_module = session.modules.daq
daq_module.device(MFLI_lockin)
daq_module.type(0)  # Continuous acquisition
daq_module.grid.mode(2)
daq_module.count(1)
daq_module.duration(VOLTAGE_DURATION)
daq_module.preview(True)
daq_module.grid.cols(num_cols)
daq_module.level(0.00000100)
daq_module.endless(0)

prober = MFLI("169.254.254.194", "DEV5149")

# Data saving setup
daq_module.save.fileformat(3)
daq_module.save.filename('zi_toolkit_acq_example')
daq_module.save.saveonread(1)

sample_node = MFLI_lockin.demods[0].sample.zi_node.lower() + ".r"
daq_module.subscribe(sample_node)
clockbase = MFLI_lockin.clockbase()

OUT_CHANNEL = 0


results = []

data_dict = DataDict(
    freq=dict(unit="Hz"),
    resistance=dict(unit="Ohm", axes=["freq"])
)

data_dict.validate()

with DDH5Writer(data_dict, measurement_name) as writer:
    writer.add_tag(tags)
    writer.backup_file([__file__, setup_file])
    writer.save_text("wiring.md", wiring)
    writer.save_dict("station_snapshot.json", station.snapshot())
    # _ = 11
    # while _ <=5e6:
    for _ in tqdm(range(11,int(5e6+1),50000)):
        # # Apply voltage 
        # MFLI_lockin.sigouts[OUT_CHANNEL].amplitudes[1].value(0.9) ## probe: 2e-3
        # MFLI_lockin.currins[IN_CHANNEL].range(100e-6)
        # MFLI_lockin.oscs[OSC_INDEX].freq(500)

        # MFLI_lockin.sigouts[OUT_CHANNEL].on(True)
        # time.sleep(VOLTAGE_DURATION)
        # MFLI_lockin.sigouts[OUT_CHANNEL].on(False)4

        MFLI_lockin.sigouts[OUT_CHANNEL].amplitudes[1].value(2e-3) ## probe: 2e-3
        MFLI_lockin.oscs[OSC_INDEX].freq(_)
        MFLI_lockin.currins[IN_CHANNEL].range(10e-6)
        # print('Start measuring resistance')
        # Measure resistance
        prober = MFLI("169.254.254.194", "DEV5149")
        Z_array = prober.measure_impedance(10, 0.2, 30e3)
        X_array = Z_array.real
        Y_array = Z_array.imag
        X_ave = np.average(X_array)
        X_std = np.std(X_array)
        Y_ave = np.average(Y_array)
        Y_std = np.std(Y_array)

        R_ave = np.sqrt(X_ave**2 + Y_ave**2)
        R_std = np.abs(X_ave/R_ave)*X_std + np.abs(Y_ave/R_ave)*Y_std

        print(f"resistance: {R_ave} +- {R_std} Ohm")

        # daq_data = daq_module.read(raw=False, clk_rate=clockbase)
        # resistance = calculate_resistance(daq_data)  # Assuming this function processes daq_data to calculate resistance
        # current = daq_data

        # results.append(resistance)
        results.append(R_ave)

        # Save data
        # writer.add_data(resistance=resistance)
        
        writer.add_data(
            freq = _,
            resistance = R_ave
        )

        # Update plot
        # writer.file.flush()
        # Assuming plottr is configured to automatically update when the file is updated
        
        # Wait for the next cycle
        # time.sleep(VOLTAGE_DURATION)

