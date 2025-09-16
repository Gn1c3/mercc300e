import os
import csv
from glob import glob

def find_col(fieldnames, options):
    for opt in options:
        if opt in fieldnames:
            return opt
    return None
//
//
//
//

def hexstr_to_bytes(data_str):
    if not isinstance(data_str, str):
        return []
    return [b for b in data_str.strip().split() if b]

def csv_to_asc(input_csv, output_asc):
    with open(input_csv, newline='') as csvfile, open(output_asc, 'w', newline='') as outfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames

        # Find columns
        timestamp_col = find_col(fieldnames, ['Start Time', 'Timestamp', 'Time', 'start_time'])
        id_col = find_col(fieldnames, ['ID', 'Id', 'id'])
        dlc_col = find_col(fieldnames, ['DLC', 'Len', 'length', 'dlc'])
        data_col = find_col(fieldnames, ['Data', 'data', 'DATA'])
        fdf_col = find_col(fieldnames, ['FDF', 'EDL'])  # CAN FD frame flag
        brs_col = find_col(fieldnames, ['BRS'])
        esi_col = find_col(fieldnames, ['ESI'])

        # ASC header
        outfile.write('date 2025-01-01 00:00:00.000\n')
        outfile.write('base hex  timestamps absolute\n')
        outfile.write('no internal events logged\n\n')

        for row in reader:
            # Time in seconds to milliseconds
            try:
                ts = float(row[timestamp_col])
            except Exception:
                ts = 0.0
            ms = ts * 1000

            canid = row.get(id_col, '0')
            try:
                canid_int = int(canid, 16) if (isinstance(canid, str) and (canid.startswith('0x') or any(c in canid for c in 'ABCDEFabcdef'))) else int(canid)
            except Exception:
                canid_int = 0
            canid_hex = f"{canid_int:X}"

            data_bytes = hexstr_to_bytes(row.get(data_col, ''))
            dlc = row.get(dlc_col, None)
            try:
                dlc_int = int(dlc, 16) if (dlc and isinstance(dlc, str) and any(c in dlc for c in 'ABCDEFabcdef')) else int(dlc) if dlc else len(data_bytes)
            except Exception:
                dlc_int = len(data_bytes)

            is_fd = row.get(fdf_col, '0') == '1' if fdf_col else False
            is_brs = row.get(brs_col, '0') == '1' if brs_col else False
            is_esi = row.get(esi_col, '0') == '1' if esi_col else False

            # ASC CAN FD frame format example:
            #   0.0000001 1 12345678x Rx d 64 01 02 ...    FD BRS ESI

            frame_type = 'Rx'
            x_fd = 'x' if is_fd else ''
            data_str = ' '.join(data_bytes[:dlc_int])
            # Add FD/flags comment if needed
            fd_flags = []
            if is_fd:
                fd_flags.append('FD')
            if is_brs:
                fd_flags.append('BRS')
            if is_esi:
                fd_flags.append('ESI')
            flag_str = ' '.join(fd_flags)

            line = f"{ms:.7f} 1 {canid_hex}{x_fd} {frame_type} d {dlc_int} {data_str}"
            if flag_str:
                line += f" {flag_str}"
            line += '\n'
            outfile.write(line)

def main():
    os.makedirs("savvycan-playback", exist_ok=True)
    csv_files = glob("*.csv")
    for csv_file in csv_files:
        base = os.path.splitext(os.path.basename(csv_file))[0]
        out_file = f"savvycan-playback/{base}_savvycan.asc"
        try:
            csv_to_asc(csv_file, out_file)
            print(f"Converted {csv_file} -> {out_file}")
        except Exception as e:
            print(f"Failed to convert {csv_file}: {e}")

if __name__ == "__main__":
    main()
