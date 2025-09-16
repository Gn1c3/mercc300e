import os
import pandas as pd

def convert_to_savvycan(csv_file_path):
    """
    Converts a CAN-FD CSV log to a SavvyCAN-compatible CSV format.

    Args:
        csv_file_path (str): The path to the CSV file to convert.

    Returns:
        pd.DataFrame: A DataFrame containing the converted data.
    """
    # Read the original CSV file
    df = pd.read_csv(csv_file_path)

    # Ensure the expected columns are processed and create new DataFrame
    savvycan_df = pd.DataFrame()
    savvycan_df['Timestamp'] = df['Timestamp']  # Adjust as necessary based on original CSV structure
    savvycan_df['ID'] = df['ID']  # Adjust as necessary based on original CSV structure
    savvycan_df['Len'] = df['Len']  # Adjust as necessary based on original CSV structure

    # Expand Data0...Data63
    for i in range(64):
        savvycan_df[f'Data{i}'] = df[f'Data{i}'] if f'Data{i}' in df else ''

    return savvycan_df

def main():
    # Create the output directory if it doesn't exist
    output_dir = 'savvycan-playback'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Iterate through all CSV files in the root directory
    for filename in os.listdir('.'):  
        if filename.endswith('.csv') and filename != 'savvycan-playback':
            savvycan_df = convert_to_savvycan(filename)
            output_file_path = os.path.join(output_dir, f"{filename.split('.')[0]}_savvycan.csv")
            savvycan_df.to_csv(output_file_path, index=False)

if __name__ == "__main__":
    main()