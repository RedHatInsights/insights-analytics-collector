import os
from insights_analytics_collector import FileSplitter, register


@register('config', '1.0', description='CONFIG', config=True)
def config(since, **kwargs):
    return {
        'version': '1.0'
    }


@register('big_table', '1.0', format='csv', description='Testing CSV data - file splitting')
def big_table(full_path, max_data_size, **kwargs):
    return _simple_csv(full_path, 'big_table', 10, max_data_size)


@register('big_table_2', '1.0', format='csv', description='Testing CSV data - file splitting 2')
def big_table_2(full_path, max_data_size, **kwargs):
    return _simple_csv(full_path, 'big_table', 3, 800)


@register('csv_collection_1', '1.0', format='csv', description='CSV 1')
def csv_collection_1(full_path, max_data_size, **kwargs):
    return _simple_csv(full_path, 'csv_collection_1', 1, max_data_size=100)


@register('csv_collection_2', '1.0', format='csv', description='CSV 2')
def csv_collection_2(full_path, max_data_size, **kwargs):
    return _simple_csv(full_path, 'csv_collection_2', 1, max_data_size=200)


@register('csv_collection_3', '1.0', format='csv', description='CSV 3')
def csv_collection_3(full_path, max_data_size, **kwargs):
    return _simple_csv(full_path, 'csv_collection_3', 1, max_data_size=300)


@register('json_collection_1', '1.0', format='json', description='JSON 1')
def json_collection_1(**kwargs):
    return {
        'json1': 'True'
    }


@register('json_collection_2', '2.0', format='json', description='JSON 2')
def json_collection_2(**kwargs):
    return {
        'json2': 'True'
    }


def _simple_csv(full_path, file_name, files_cnt, max_data_size):
    file_path = _get_file_path(full_path, file_name)
    file = FileSplitter(filespec=file_path, max_file_size=max_data_size)
    header = "Col1,Col2\n"
    line = "1234,6789\n"

    # create required number of files (decrease by headers - it's CSV)
    file.write(header)
    for _ in range(files_cnt * int(max_data_size/10) - files_cnt):
        file.write(line)

    return file.file_list()


def _get_file_path(path, table):
    return os.path.join(path, table + '_table.csv')
