import pandas as pd
import os

if __name__ == "__main__":
    input_file = 'data/Workbook.xlsx'
    output_file = 'data/Workbook_merged.xlsx'

    # Read each sheet of the Excel workbook into a pandas DataFrame
    xls = pd.ExcelFile(input_file)
    sheet_names = xls.sheet_names
    dfs = []

    # Read each sheet and append its DataFrame to the list
    for sheet_name in sheet_names:
        df = xls.parse(sheet_name)
        # Ensure 'key' column is string before cleaning
        df['key'] = df['key'].astype(str).str.strip().str.lower()
        dfs.append(df)

    # Merge DataFrames based on the 'key' column
    merged_df = dfs[0]
    for idx, df in enumerate(dfs[1:], start=1):
        merged_df = pd.merge(
            merged_df,
            df,
            on='key',
            how='outer',
            suffixes=('', f'_{sheet_names[idx]}')
        )

    # Sort and reset index
    merged_df.sort_values(by='key', inplace=True)
    merged_df.reset_index(drop=True, inplace=True)

    # Write the merged DataFrame to a new Excel file in the same directory
    merged_df.to_excel(output_file, index=False)
    print(f"Merged Excel file saved successfully as {output_file}.")
