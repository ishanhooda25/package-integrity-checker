"""Signal detection for suspicious code patterns."""

import re


def _find_dynamic_calls(rel_file, text):
    """Find eval(), exec(), os.system() calls in text.

    Args:
        rel_file: relative path of file containing code
        text: text to scan

    Returns:
        list of signal dicts
    """
    signals = []
    
    # eval calls
    pattern = r'eval\s*\('
    if re.search(pattern, text):
        snippet = text[:120]
        signals.append({
            'file': rel_file,
            'line': text.count('\n'),
            'kind': 'dynamic_exec',
            'snippet': snippet,
            'severity': 'high',
        })
    
    # exec calls
    pattern = r'exec\s*\('
    if re.search(pattern, text):
        snippet = text[:120]
        signals.append({
            'file': rel_file,
            'line': text.count('\n'),
            'kind': 'dynamic_exec',
            'snippet': snippet,
            'severity': 'high',
        })
    
    # shell commands
    pattern = r'os\.system\s*\('
    if re.search(pattern, text):
        signals.append({
            'file': rel_file,
            'line': text.count('\n'),
            'kind': 'shell_exec',
            'snippet': text[:120],
            'severity': 'high'
        })
    
    return signals


def _check_network_calls(rel_file, text):
    """Find network calls like urllib.request.urlopen, requests.get.

    Args:
        rel_file: relative path of file containing code
        text: text to scan

    Returns:
        list of signal dicts
    """
    signals = []
    
    # urllib.request.urlopen patterns
    pattern = r'urllib\.request\.urlopen\s*\('
    if re.search(pattern, text):
        snippet = text[:120]
        signals.append({
            'file': rel_file,
            'line': text.count('\n'),
            'kind': 'network_call',
            'snippet': snippet,
            'severity': 'high'
        })
    
    return signals


def scan_text(relpath, text):
    """Scan text for suspicious patterns.

    Returns a list of dicts with keys:
      - "file": relative path
      - "line": line number (approximate)
      - "kind": one of "network_call", "shell_exec", "dynamic_exec", "encoded_blob"
      - "snippet": max 120 chars of suspicious code
      - "severity": low | medium | high

    Args:
        relpath: relative path of file containing code
        text: text to scan

    Returns:
        list of signal dicts
    """
    signals = []
    
    # Check for dynamic execution patterns first (eval, exec)
    found_dynamic = _find_dynamic_calls(relpath, text)
    if found_dynamic:
        signals.extend(found_dynamic)
        return signals
    
    # Check for shell commands (os.system)
    pattern = r'os\.system\s*\('
    if re.search(pattern, text):
        signal = {
            'file': relpath,
            'line': text.count('\n'),
            'kind': 'shell_exec',
            'snippet': text[:120],
            'severity': 'high'
        }
        signals.append(signal)
        return signals
    
    # Check for network calls (urllib, requests)
    found_network = _check_network_calls(relpath, text)
    if found_network:
        signals.extend(found_network)
        return signals
    
    # If no results and the text is long enough, check for encoded blobs
    if not signals and len(text) >= 200:
        # Look for long base64/hex strings (200+ chars)
        b64_pattern = r'[A-Za-z0-9_-]{200,}='
        matches = re.findall(b64_pattern, text)

        if matches:
            signal = {
                'file': relpath,
                'line': text.count('\n'),
                'kind': 'encoded_blob',
                'snippet': text[:120],
                'severity': 'high',
            }
            signals.append(signal)

    return signals


def scan_file(path, relpath):
    """Scan a file for suspicious patterns. Skip binary/unreadable files.

    Args:
        path: full path to file
        relpath: relative path of file

    Returns:
        list of signal dicts, or empty list if file is unreadable/binary
    """
    
    try:
        # Check if file is readable
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        
        return scan_text(relpath, text)
    except (PermissionError, UnicodeDecodeError):
        return []
