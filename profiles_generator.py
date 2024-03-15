from tools_libs import pd

def profiles_generator(students_csv, transcripts_csv):
    # read the csv files
    students_df    = pd.read_csv(students_csv)
    transcripts_df = pd.read_csv(transcripts_csv)

    # merge the two dataframes
    merged_df = pd.concat([students_df, transcripts_df], axis=1)

    return merged_df