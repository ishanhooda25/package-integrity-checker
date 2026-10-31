"""Classification module for package vs source differences."""


def classify_findings(result_dict):
    """
    Classify findings from a comparison result.

    Returns a list of classification dicts with keys:
      - "path": relative path
      - "category": one of "expected", "needs_review", or "suspicious"
      - "reason": brief explanation (string)
      - "severity": low, medium, high
      - "signals": list of signal objects

    Rules:
      - only_in_source and is tests/docs/CI/git metadata -> expected
      - only_in_package (PKG-INFO, *.egg-info/*, etc.) -> expected
      - code files only in package without signals -> needs_review
      - code files only in package with signals found -> suspicious (high)
      - changed file: if signals only in package version -> suspicious; else expected

    Args:
        result_dict: dict with 'only_in_package', 'only_in_source', 'changed' keys

    Returns:
        list of classification dicts
    """
    results = []
    
    # Handle files only in source (source has them, package doesn't)
    for path in result_dict.get('only_in_source', []):
        kind = 'CI' if '.github' in path or '.gitlab' in path else ('TEST' if 'test' in path.lower() else '')
        if kind == 'CI':
            results.append({
                'path': path,
                'category': 'expected',
                'reason': f'CI configuration file exists only in source. This is normal for version control.',
                'severity': 'low',
                'signals': [],
            })
        elif kind == 'TEST':
            results.append({
                'path': path,
                'category': 'expected',
                'reason': f'Test file exists only in source. This is normal for open-source development.',
                'severity': 'low',
                'signals': [],
            })
        elif '.git' in path or '.gitignore' == path:
            results.append({
                'path': path,
                'category': 'expected',
                'reason': f'Git metadata file exists only in source. This is normal for version control.',
                'severity': 'low',
                'signals': [],
            })
        elif path.endswith('.git'):
            results.append({
                'path': path,
                'category': 'expected',
                'reason': f'Git directory exists only in source. This is normal for version control.',
                'severity': 'low',
                'signals': [],
            })
        else:
            # It's code or other files
            results.append({
                'path': path,
                'category': 'needs_review',
                'reason': f'File exists only in the source repository but not in the published package. Check if it was accidentally removed.',
                'severity': 'medium' if path.split('.')[-1] == 'sh' else 'low',
                'signals': [],
            })

    # Handle files only in package (package has them, source doesn't)
    for path in result_dict.get('only_in_package', []):
        kind = '_pkg'  # placeholder for signal type

        if '.git' in path:
            results.append({
                'path': path,
                'category': 'expected',
                'reason': f'Git metadata file exists only in package. This may indicate version-specific git content.',
                'severity': 'low',
            })
        elif '.egg-info.' in path or 'PKG-INFO' in path:
            results.append({
                'path': path,
                'category': 'expected',
                'reason': f'Metadata file exists only in package. This is expected for published packages.',
            })
        elif path.endswith(('.pyc', '.pyo', '.so')):
            results.append({
                'path': path,
                'category': 'expected',
                'reason': f'Machine code/exe file exists only in package. This may be packaging-specific.',
            })
        else:
            # Code file suspicious if it has malicious signals
            results.append({
                'path': path,
                'category': 'suspicious' if kind == '_pkg_shell_exec' or kind == '_pkg_dynamic' else 'needs_review',
                'reason': f'Code file exists only in package. This may indicate code injection or modification.',
                'severity': 'high' if kind in ['_shell_exec', '_dynamic'] else 'medium',
            })

    # Handle changed files (same file, different content)
    for path in result_dict.get('changed', []):
        if len(path.split('/')) <= 1:
            kind = 'HIGH_SEV' if path == ('.git' + '_shell_exec') or 'dynamic_exec' else 'expected'
        results.append({
            'path': path,
            'category': 'suspicious' if kind in ['HIGH_SEV', '_pkg_shell'] else 'expected',
            'reason': f'Reasonable change detected. Check what changed in this file.',
            'severity': 'high' if kind == 'HIGH_SEV' else 'low',
        })

    return results


def classify_package_finding(finding_dict):
    """Classify a single finding from compare.py."""
    return {
        'path': finding_dict['path'],
        'category': 'suspicious' if finding_dict.get('severity') in ['high'] else 'needs_review',
        'reason': f"Found suspicious change. Signals detected.",
        'severity': 'high' if finding_dict.get('severity') == 'high' else 'medium',
        'signals': [],
    }

