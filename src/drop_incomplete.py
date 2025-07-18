def read_csv(file_path):
    import pandas as pd
    data = pd.read_csv(file_path)
    return data

def manipulate_data(data):
    # Drop rows with any missing values.
    cleaned_data = data.dropna()
    return cleaned_data

def output_results(data, output_path):
    data.to_csv(output_path, index=False)

if __name__ == "__main__":
    input_file = 'data/drop_incomplete_in.csv'
    output_file = 'data/drop_incomplete_out.csv'
    
    # Read the CSV file.
    data = read_csv(input_file)
    
    # Manipulate the data.
    cleaned_data = manipulate_data(data)
    
    # Output the results.
    output_results(cleaned_data, output_file)