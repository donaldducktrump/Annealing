import os

import numpy as np
from plottr.data.datadict_storage import DataDict, DDH5Writer
from tqdm import tqdm

from setup_sweeper import *

import logging
import sys

measurement_name = os.path.basename(__file__)[:-3]

# Specify the number of sweeps to perform back-to-back.
LOOPCOUNT = 1

sweeper = session.modules.sweeper
sweeper.device(MFLI_lockin)

sweeper.gridnode(MFLI_lockin.oscs[OSC_INDEX].freq)
sweeper.start(1e3)
sweeper.stop(5e6) # 500e3 for MF devices, 50e6 for others
sweeper.samplecount(100)
sweeper.xmapping(0)
sweeper.bandwidthcontrol(2)
sweeper.bandwidthoverlap(0)
sweeper.scan(0)
sweeper.loopcount(LOOPCOUNT)
sweeper.settling.time(0)
sweeper.settling.inaccuracy(0.001)
sweeper.averaging.tc(1)
sweeper.averaging.sample(20)
sweeper.averaging.sample(1)

## demodulation setup
MFLI_lockin.demods[DEMOD_INDEX].order(3)
MFLI_lockin.demods[DEMOD_INDEX].sinc(1)
MFLI_lockin.demods[DEMOD_INDEX].enable(1)
MFLI_lockin.demods[DEMOD_INDEX].adcselect(IN_CHANNEL+1)
MFLI_lockin.demods[DEMOD_INDEX].rate(1674)

sweeper.save.filename('sweep_with_save')
sweeper.save.fileformat('hdf5')

# sample_nodes = [
#     MFLI_lockin.device.demods[0].sample.zi_node.lower() + ".x",
#     MFLI_lockin.device.demods[0].sample.zi_node.lower() + ".y"
# ]

handler = logging.StreamHandler(sys.stdout)
logging.getLogger("zhinst.toolkit").setLevel(logging.INFO)
logging.getLogger("zhinst.toolkit").addHandler(handler)

sample_node = MFLI_lockin.demods[DEMOD_INDEX].sample
sweeper.subscribe(sample_node)

def freq_sweep():
    MFLI_lockin.sigouts[OUT_CHANNEL].on(True)
    sweeper.save.saveonread(True)
    sweeper.execute()
    print(f"Perform {LOOPCOUNT} sweeps")
    try:
        while sweeper.progress() < 1.0:
            print(f"progress {sweeper.progress()*100}%")
            sweep_data = sweeper.read()
            time.sleep(0.1)
    finally:
        sweep_data = sweeper.read()
        MFLI_lockin.sigouts[OUT_CHANNEL].on(False)
        sweeper.unsubscribe(sample_node)
        return sweep_data

data = DataDict(
    freq=dict(unit="Hz"),
    amp = dict(unit = 'V', axes = ["freq"])
)
data.validate()

with DDH5Writer(data, data_path, name = measurement_name) as writer:
    writer.add_tag(tags)
    writer.backup_file([__file__, setup_file])
    writer.save_text("wiring.md", wiring)
    writer.save_dict("station_snapshot.json", station.snapshot())
    sweep_data = freq_sweep()
    writer.add_data(
        freq = sweep_data[sample_node][0][0]["frequency"],
        amp = sweep_data[sample_node][0][0]["r"]
    )

# freq = sweep_data[sample_node][0][0]["frequency"],
# amp = sweep_data[sample_node][0][0]["r"]
# print(sum(amp)/len(amp))