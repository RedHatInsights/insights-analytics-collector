import os

from insights_analytics_collector import CsvFileSplitter


def trivial_slicing(key, since, until, last_gather):
    return [(since, until)]


def simple_csv(full_path, file_name, files_cnt, max_data_size):
    file_path = get_file_path(full_path, file_name)
    file = CsvFileSplitter(filespec=file_path, max_file_size=max_data_size)
    header = "Col1,Col2\n"
    line = "1234,6789\n"

    # create required number of files (decrease by headers - it's CSV)
    file.write(header)
    for _ in range(files_cnt * int(max_data_size / 10) - files_cnt):
        file.write(line)

    return file.file_list()


def get_file_path(path, table):
    return os.path.join(path, table + "_table.csv")
