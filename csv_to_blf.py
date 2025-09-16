import csv
from asammdf import MDF, CANDataFrame
import numpy as np

def hexstr_to_bytes(row, start_idx, length):
    data = []
    for i in range(start_idx, start_idx + length):
        val = row[i].strip()
        if val:
            data.append(int(val, 16))
        else:
            break
    return data

input_csv = "your_input.csv"
output_blf = "output.blf"

with open(input_csv, newline='') as csvfile:
    reader = csv.reader(csvfile)
    header = next(reader)
    id_idx = header.index("ID")
    ts_idx = header.index("Timestamp")
    len_idx = header.index("LEN")
    data_start = len_idx + 1

    frames = []
    for row in reader:
        can_id = int(row[id_idx], 16) if 'x' in row[id_idx] or row[id_idx].startswith('0x') else int(row[id_idx])
        ts = float(row[ts_idx])
        dlc = int(row[len_idx])
        data = hexstr_to_bytes(row, data_start, dlc)
        # For CAN FD, set flags accordingly
        frame = CANDataFrame(
            timestamp=ts,
            arbitration_id=can_id,
            data=bytes(data),
            is_fd=True,
            is_extended_id=True if can_id > 0x7FF else False,
            bitrate_switch=True,
        )
        frames.append(frame)

mdf = MDF()
mdf.append(frames)
mdf.save(output_blf, overwrite=True)
print(f"Saved {len(frames)} frames to {output_blf}")