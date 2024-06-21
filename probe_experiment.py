import os
import time
import statistics


import numpy as np
from plottr.data.datadict_storage import DataDict, DDH5Writer
from tqdm import tqdm

from setup_probe import *

measurement_name = os.path.basename(__file__)[:-3]

# sample_nodes = [
#     MFLI_lockin.demods[DEMOD_INDEX].sample.x,
#     MFLI_lockin.demods[DEMOD_INDEX].sample.y
# ]

TOTAL_DURATION = 5  # 秒
SAMPLING_RATE = 30  # サンプル/秒
BURST_DURATION = 5  # 秒ffff

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
daq_module.execute()

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

data_dict = DataDict(
    time=dict(unit="s"),
    amp=dict(unit="V", axes=["time"])
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

with DDH5Writer(data_dict, data_path, name = measurement_name) as writer:
    writer.add_tag(tags)
    writer.backup_file([__file__, setup_file])
    writer.save_text("wiring.md", wiring)
    writer.save_dict("station_snapshot.json", station.snapshot())
    writer.add_data(
        time = daq_data[sample_node][0][2],
        amp = daq_data[sample_node][0][1],
    )

cleaned_list = [x for x in daq_data[sample_node][0][1][0] if str(x) != 'nan']
# print(cleaned_list)
print(f'amp(A)={statistics.mean(list(cleaned_list))}')