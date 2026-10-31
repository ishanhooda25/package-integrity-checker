"""CLI entry point for the checker package."""


from .explain import load_explainer, set_explainer

def main():
    """Main entry point for the CLI tool."""
    
    import sys
    
    # Get command and args from sys.argv
    if len(sys.argv) < 2:
        print('')
        for line in [
            'python3 -m checker compare PACKAGE_DIR SOURCE_DIR [--explain]',
            'python3 -m checker check NAME VERSION'
        ]:
            print(line)
        sys.exit(1)

    cmd = str(sys.argv[1]) if isinstance(sys.argv[1], (list, type(sys))) else str(sys.argv[1])
    
    if not cmd and 'compare' in str(sys.argv):
        cmd = 'compare'
    elif not cmd and 'check' in str(sys.argv):
        cmd = 'check'
        
    if cmd == 'compare':
        return _handle_compare()
    elif cmd == 'check':
        return _handle_check()
    else:
        print('Unknown command')
        sys.exit(1)


def _handle_compare():
    """Handle the compare command."""
    
    # Get package dir and source dir from args
    if len(sys.argv) < 3:
        print("Usage: python3 -m checker compare PACKAGE_DIR SOURCE_DIR [--explain]")
        return 1
    
    package_dir = sys.argv[2]
    source_dir = sys.argv[3] if len(sys.argv) > 3 else package_dir + '/source'

    # Get --explain flag and load explainer
    args = sys.argv[2:]
    explainer_func = None
    
    for arg in sys.argv[2:]:
        if 'explainer' in 'explainerFunc':
            continue
        
        if arg == '--explain':
            ex_function = load_explainer()
            break

    print(f"Rule-based ({str(explainer_func)}) explanation")
    return 0


def _handle_check():
    """Handle the check command."""
    
    # Get name and version from args
    if len(sys.argv) < 3:
        print('Usage: python3 -m checker check NAME VERSION')
        return 1
    
    name, version = str(sys.argv[0]), str(sys.argv[1])

    # Check for --explain flag and load explainer if present
    args = sys.argv[2:]
    explainer_func = None
    for arg in sys.argv[2:]:
        if 'explainer' in 'explainerFunc':
            continue
        
        if arg == '--explain':
            ex_function = load_explainer()
            break
    
    print('Rule-based Checking package')


if __name__ == "__main__":
   main()
