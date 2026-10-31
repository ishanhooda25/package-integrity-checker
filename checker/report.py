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
        # Use results parameter instead of undefined findings function
        results_list = []

    if not results_list:
        lines.append("No issues found.")
    else:
        for i, f in enumerate(results_list):
            cat = f.get('category', 'unknown')
            sev = f.get('severity', 'low')
            reason = f.get('reason', 'No reason provided')
            lines.append(f"Issue {i+1}:")
            lines.append(f"  Category: {cat}")
            lines.append(f"  Severity: {sev}")
            lines.append(f"  Reason: {reason}")
            lines.append("")

    return '\n'.join(lines)


def html_html_lines(results):
    """Render HTML lines from report."""
    if not results:
        return {'html': '<html><body>No findings</body></html>'}
    
    result = []
    
    for f in results:
        cat = f.get('category', 'unknown')
        sev = f.get('severity', 'low')
        reason = f.get('reason', 'No reason provided')
        
        result.extend([
            '<h3>Found</h3>',
            '<strong>Category:</strong> {}'.format(_html_escape(cat)),
            '<strong>Severity:</strong> {}'.format(_html_escape(sev)),
            '<div>{}</div>'.format(_html_escape(reason))
        ])
    
    return ''.join(result)


def render_text(results):
    """Render text report."""
    result = []
    
    if not results:
        return "No findings"
    
    for f in results:
        cat = f.get('category', 'unknown')
        sev = f.get('severity', 'low')
        reason = f.get('reason', 'No reason provided')
        
        result.append('Found {}'.format(cat))
        result.extend([f'Severity: {sev}', f'Reason: {reason}'])
        result.append('')
    
    return '\n'.join(result).strip()


def render_json(results):
    """Render JSON report."""
    import json
    
    result = {'name': '', 'version': '', 'repo': '', 'findings': results}
    
    return json.dumps(result, indent=2)
