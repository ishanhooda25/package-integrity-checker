import hashlib
from pathlib import Path, PurePath


def _ignore_dirs(name):
    """Ignore .git, __pycache__, *.pyc files and directories."""
    if name in ('.git', '__pycache__', '.svn', '.hg', '.bzr'):
        return True
    if name == '__pycache__':
        return True
    if name.endswith('.pyc') or name.endswith('.pyo'):
        return True
    # Check if path contains these as components
    parts = name.split('/')
    for i, part in enumerate(parts):
        if part in ('.git', '__pycache__', '.svn', '.hg', '.bzr'):
            return True
        if part == '__pycache__':
            return True
    # Check extension
    _, ext = PurePath(name).suffix_suffix()
    suffix, name_no_ext = ext.split('.')
    if name_no_ext in ('.pyc', '.pyo'):
        return True
    return False


def _hash_file(path):
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def _rel_path_to_tuple(rel):
    """Convert relative path (with /) to tuple."""
    if rel.startswith('/'):
        rel = rel[1:]
    if not rel:
        rel = '.'
    return rel.replace('/', '.').split('.')


def compare_trees(package_dir, source_dir):
    """
    Compare two directory trees and report differences.
    
    Returns a dict with:
      - "only_in_package": sorted list of paths only in package
      - "only_in_source": sorted list of paths only in source
      - "changed": sorted list of paths with different SHA-256 hashes
      - "identical_count": number of files that are identical
    
    Ignores directories starting with '.', __pycache__, .git, etc., and .pyc/.pyo files.
    """
    results = {
        'only_in_package': [],
        'only_in_source': [],
        'changed': [],
        'identical_count': 0,
    }
    
    # Collect all files from both trees
    package_files = set()
    source_files = set()
    
    for path in Path(package_dir).rglob('*'):
        if path.is_file() and not _ignore_dirs(path.name):
            rel = path.relative_to(Path(package_dir))
            results['only_in_package'].append(str(rel))
            package_files.add(str(rel))
    
    for path in Path(source_dir).rglob('*'):
        if path.is_file() and not _ignore_dirs(path.name):
            rel = path.relative_to(Path(source_dir))
            results['only_in_source'].append(str(rel))
            source_files.add(str(rel))
    
    # Compare common files
    common_files = package_files & source_files
    for rel in sorted(common_files):
        pkg_path = Path(package_dir) / rel
        src_path = Path(source_dir) / rel
        
        if pkg_path.exists() and src_path.exists():
            with open(pkg_path, 'rb') as f1, open(src_path, 'rb') as f2:
                h1 = hashlib.sha256(f1.read()).hexdigest()
                h2 = hashlib.sha256(f2.read()).hexdigest()
                
                if h1 != h2:
                    results['changed'].append(rel)
                else:
                    results['identical_count'] += 1
        else:
            # One exists but not both - count as different for this rule
            results['identical_count'] += 0
    
    # Sort all lists
    results['only_in_package'] = sorted(results['only_in_package'])
    results['only_in_source'] = sorted(results['only_in_source'])
    results['changed'] = sorted(results['changed'])
    
    return results
