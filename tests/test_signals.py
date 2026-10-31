"""Tests for signals module."""


def _test_long_string():
    """Helper to create strings with 200+ base64-like chars."""
    # Create a string with 250 A's followed by '=' (simulating long base64)
    return 'A' * 250 + '='


def test_scan_text_network_call():
    """Test detection of network_call signals."""
    from checker.signals import scan_text
    
    text = '''
import urllib.request
response = urllib.request.urlopen("https://evil.com")
'''
    
    result = scan_text('test.py', text)
    assert any(x['kind'] == 'network_call' for x in result), "Should detect network calls"


def test_scan_text_dynamic_exec():
    """Test detection of dynamic execution."""
    from checker.signals import scan_text
    
    text = '''
code = input("Enter code")
eval(code)
'''
    
    result = scan_text('test.py', text)
    assert any(x['kind'] == 'dynamic_exec' for x in result), "Should detect eval()"


def test_scan_text_shell_exec():
    """Test detection of shell command execution."""
    from checker.signals import scan_text
    
    text = '''
import os
os.system("rm -rf /")
'''
    
    result = scan_text('test.py', text)
    assert any(x['kind'] == 'shell_exec' for x in result), "Should detect shell commands"


def test_scan_text_encoded_blob():
    """Test detection of long base64/hex strings."""
    from checker.signals import scan_text
    
    # Create a string with 250 A's followed by '=' (simulating long base64 payload)
    long_string = 'A' * 250 + '='
    
    text = f'''
# Malicious payload data embedded in code to evade detection
{long_string}
'''
    
    result = scan_text('test.py', text)
    assert any(x['kind'] == 'encoded_blob' for x in result), "Should detect long base64 strings"


def test_scan_file_binary_skipped(tmp_path):
    """Test that binary files are skipped."""
    from checker.signals import scan_file
    
    # Create a binary file (just empty bytes)
    binary_file = tmp_path / 'binary.dat'
    binary_file.write_bytes(b'\x00\x01\x02\x03')
    
    result = scan_file(str(binary_file), 'test_file.dat')
    assert isinstance(result, list), "Should return a list of signals"
