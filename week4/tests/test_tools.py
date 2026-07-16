from src.tools import read_file


def test_read_txt_file(tmp_path):
    """Test reading a .txt file."""
    test_file = tmp_path / 'test.txt'
    test_file.write_text('Hello this is a test file.')
    result = read_file(str(test_file))
    assert 'Hello this is a test file.' in result


def test_read_missing_file():
    """Test reading a file that does not exist."""
    result = read_file('nonexistent_file.txt')
    assert 'File not found' in result


def test_read_unsupported_format(tmp_path):
    """Test reading unsupported file format."""
    test_file = tmp_path / 'test.csv'
    test_file.write_text('col1,col2')
    result = read_file(str(test_file))
    assert 'Unsupported file type' in result


def test_read_empty_txt_file(tmp_path):
    """Test reading an empty .txt file."""
    test_file = tmp_path / 'empty.txt'
    test_file.write_text('')
    result = read_file(str(test_file))
    assert result == ''
