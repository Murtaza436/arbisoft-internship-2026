from src.tools import read_file


def test_read_existing_file(tmp_path):
    test_file = tmp_path / 'test.txt'
    test_file.write_text('Hello world')
    result = read_file(str(test_file))
    assert 'Hello world' in result


def test_read_missing_file():
    result = read_file('nonexistent.txt')
    assert 'File not found' in result


def test_read_unsupported_format(tmp_path):
    test_file = tmp_path / 'test.csv'
    test_file.write_text('col1,col2')
    result = read_file(str(test_file))
    assert 'Unsupported' in result
