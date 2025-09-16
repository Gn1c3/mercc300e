import os
import csv
from glob import glob

def hexstr_to_bytes(data_str):
    """Convert a hex string like '39 0E 00' to a list of ints."""
    if not isinstance(data_str, str):
        return []
    data_str = data_str.strip().replace("  ", " ")
    if not data_str:
        return []
    # Split by spaces, ignoring empty elements
    return [int(b, 16) for b in data_str.split() if b]

def find_col(fieldnames, options):
    """Return the first matching column name from options, or None."""
    for opt in options:
        if opt in fieldnames:
            return opt
    return None

def csv_to_savvycan(input_csv, output_csv):
    with open(input_csv, newline='') as csvfile, open(output_csv, 'w', newline='') as outfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames

        # Find closest matching columns
        timestamp_col = find_col(fieldnames, ['Start Time', 'Timestamp', 'Time', 'start_time'])
        id_col = find_col(fieldnames, ['ID', 'Id', 'id'])
        dlc_col = find_col(fieldnames, ['DLC', 'Len', 'length', 'dlc'])
        data_col = find_col(fieldnames, ['Data', 'data', 'DATA'])

        # Setup SavvyCAN columns
        savvycan_fields = ['Timestamp', 'ID', 'Len'] + [f'Data{i}' for i in range(64)]
        writer = csv.DictWriter(outfile, fieldnames=savvycan_fields)
        writer.writeheader()

        for row in reader:
            try:
                ts = float(row[timestamp_col])
            except Exception:
                ts = 0.0

            canid = row.get(id_col, '0')
            # Accept 0x-prefixed, hex, or decimal
            try:
                canid_int = int(canid, 16) if (isinstance(canid, str) and (canid.startswith('0x') or any(c in canid for c in 'ABCDEFabcdef'))) else int(canid)
            except Exception:
                canid_int = 0

            dlc = row.get(dlc_col, None)
            try:
                dlc_int = int(dlc, 16) if (dlc and isinstance(dlc, str) and any(c in dlc for c in 'ABCDEFabcdef')) else int(dlc) if dlc else None
            except Exception:
                dlc_int = None

            data_bytes = hexstr_to_bytes(row.get(data_col, ''))

            outrow = {
                'Timestamp': ts,
                'ID': canid_int,
                'Len': dlc_int if dlc_int is not None else len(data_bytes),
            }
            for i in range(64):
                outrow[f'Data{i}'] = data_bytes[i] if i < len(data_bytes) else ''

            writer.writerow(outrow)

def main():
    os.makedirs("savvycan-playback", exist_ok=True)
    csv_files = glob("*.csv")
    for csv_file in csv_files:
        base = os.path.splitext(os.path.basename(csv_file))[0]
        out_file = f"savvycan-playback/{base}_savvycan.csv"
        try:
            csv_to_savvycan(csv_file, out_file)
            print(f"Converted {csv_file} -> {out_file}")
        except Exception as e:
            print(f"Failed to convert {csv_file}: {e}")

if __name__ == "__main__":
    main()
