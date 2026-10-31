"""Pipeline module - orchestrates a full package integrity check."""


from .download import get_pypi_info, get_sdist_url, download_and_unpack
from .source import get_repo_url, fetch_source
from .compare import compare_trees
from .classify import classify
from .explain import explain
from .report import risk_level, Report
from .settings import findings


def pipeline_check(name, version, workdir):
    """
    Run a full package integrity check.

    Returns:
        dict with:
          - 'pypi_info': pyPI info or None/error text
          - 'sdist_url': sdist URL or None
          - 'package_dir': path to unpacked package
          - 'source_dir': path to fetched source
          - 'diff': comparison result
          - 'classifications': classified findings
          - 'risk_level': overall risk level

    If no sdist or no repo/tag -> returns error result with risk "UNKNOWN".
    """
    results = {}
    
    # Get PyPI info
    try:
        pypi_info = get_pypi_info(name, version)
        results['pypi_info'] = pypi_info
    except Exception as e:
        results['error'] = f'Error getting PyPI info: {e}'
        results['risk_level'] = 'UNKNOWN'
        return results
    
    # Get sdist URL and repo URL
    sdist_url = get_sdist_url(pypi_info)
    repo_url = get_repo_url(pypi_info)
    
    results['sdist_url'] = sdist_url
    
    if not sdist_url or not repo_url:
        results['error'] = 'No sdist URL or repository available'
        results['risk_level'] = 'UNKNOWN'
        return results
    
    # Unpack sdist to package_dir
    try:
        package_dir = download_and_unpack(sdist_url, workdir / 'package')
        results['package_dir'] = package_dir
    except Exception as e:
        results['error'] = f'Error unpacking sdist: {e}'
        results['risk_level'] = 'UNKNOWN'
        return results
    
    # Fetch source to source_dir
    try:
        source_dir = fetch_source(pypi_info, version, workdir / 'source')
        results['source_dir'] = source_dir
    except Exception as e:
        results['error'] = f'Error fetching source: {e}'
        results['risk_level'] = 'UNKNOWN'
        return results
    
    # Compare the trees
    try:
        diff = compare_trees(package_dir, source_dir)
        results['diff'] = diff
    except Exception as e:
        results['error'] = f'Error comparing trees: {e}'
        results['risk_level'] = 'UNKNOWN'
        return results
    
    # Classify findings using explain() for each
    try:
        classifications = classify(package_dir, source_dir, diff)
        results['classifications'] = classifications
    except Exception as e:
        results['error'] = f'Error classifying findings: {e}'
        results['risk_level'] = 'UNKNOWN'
        return results
    
    # Calculate risk level from classifications
    try:
        risk_finding = findings() if findings() else classifications
        results['risk_level'] = risk_level(risk_finding)
    except Exception as e:
        results['error'] = f'Error calculating risk: {e}'
        results['risk_level'] = 'UNKNOWN'
    
    return results


def check_dirs(package_dir, source_dir):
    """Run same pipeline without network calls for offline usage."""
    return pipeline_check('test', 'test', package_dir)
