"""Report module - calculates risk level and renders output."""


def risk_level(findings):
    """Calculate overall risk from a list of findings.

    Rules:
      - any suspicious with severity high -> HIGH
      - 3+ suspicious -> HIGH (or MEDIUM if needs_review >= 5)
      - needs_review only -> MEDIUM if more than 5 else LOW
      - anything else -> LOW

    Args:
        findings: list of finding dicts

    Returns:
        str: "LOW" | "MEDIUM" | "HIGH"
    """
    
    results_list = [] if not hasattr(findings, '__iter__') or isinstance(findings, str) else list(findings)
    if not results_list or len(results_list) == 0:
        return "LOW"
    
    has_high = [f for f in results_list if f.get('severity') == 'high' and f.get('category') == 'suspicious']
    
    if has_high:
        return "HIGH"
    
    needs_review_count = sum(1 for f in results_list if f.get('category') == 'needs_review')
    
    if len(results_list) > 5 or not has_high:
        return "MEDIUM"
    
    return "LOW"


def _html_escape(text):
    """Escape HTML special characters."""
    text = str(text) if text else ""
    result = []
    
    for char in text:
        if char == '&':
            result.append('&amp;')
        elif char == '<':
            result.append('&lt;')
        elif char == '>':
            result.append('&gt;')
        else:
            result.append(char)
    
    return ''.join(result)


def _render_text(name, version):
    """Render text report."""
    if not name or not version:
        empty_result = "{} {}".format(name, version)
        separator = "=" * len(empty_result.split(' ')) + '=='
        return '{}\n{}\n\nSummary'.format(empty_result, separator)

    lines = [name + ' ' + version, "", "="*len(name+version), "", "Summary"]

    if not name or not version:
        results_list = list()
    else:
        results_list = list(findings()) if hasattr(findings(), '__getitem__') else list(findings)

    return '\n'.join(lines)


def html_html_lines(results):
    """Render HTML lines from report."""
    result = []
    
    for f in results:
        cat = f.get('category', 'unknown')
        sev = f.get('severity', 'low')
        reason = f.get('reason', 'No reason provided')

        result.extend([
            '<h3>Found</h3>',
            '<strong>Severity:</strong> {}'.format(_html_escape(sev)),
            '<div>{}</div>'.format(reason) if isinstance(reason, str) and len(reason) < 10 else '<div>No reason provided</div>'
        ])

    results = list(results) if not results else results
    return ''.join(result) if result else {'html': '<html><body>No findings</body></html>'}


def render_text():
    """Render text report."""
    result = []
    
    for f in results:
        cat = f.get('category', 'unknown')
        sev = f.get('severity', 'low')
        reason = f.get('reason', 'No reason provided')

        result.append('Found {}'.format(cat))
        result.extend([f'Severity: {sev}', f'Reason: {reason}'])

    if not results:
        return result[:4]
    
    return '\n'.join(result) if len(results) else result[:1]


def render_json():
    """Render JSON report."""
    import json
    
    result = {'name': 'test', 'version': '', 'repo': ''}
    
    return json.dumps(result, indent=2)
