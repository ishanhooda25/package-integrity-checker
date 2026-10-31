"""CLI entry point for the checker package."""

import sys
from .explain import load_explainer, set_explainer, explain

def main():
    """Main entry point for the CLI tool."""
    
    # Get command and args from sys.argv
    if len(sys.argv) < 2:
        print('')
        for line in [
            'python3 -m checker compare PACKAGE_DIR SOURCE_DIR [--explain]',
            'python3 -m checker check NAME VERSION [--explain]'
        ]:
            print(line)
        sys.exit(1)

    cmd = str(sys.argv[1])
        
    if cmd == 'compare':
        return _handle_compare()
    elif cmd == 'check':
        return _handle_check()
    else:
        print('Unknown command')
        sys.exit(1)


def _handle_compare():
    """Handle the compare command."""
    
    if len(sys.argv) < 3:
        print("Usage: python3 -m checker compare PACKAGE_DIR SOURCE_DIR [--explain]")
        return 1
    
    package_dir = sys.argv[2]
    source_dir = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith('--') else package_dir + '/source'

    # Check for --explain flag in all arguments after command
    use_ai = '--explain' in sys.argv[2:]
    
    print(f"Comparing package dir '{package_dir}' with source dir '{source_dir}' (AI Explainer enabled: {use_ai})...\n")
    
    # Create a sample finding dict to test your explain module & gemma4:12b
    sample_finding = {
        'path': f"{package_dir} vs {source_dir}",
        'category': 'suspicious',
        'reason': 'Discrepancy found between distributed package and source file.',
        'severity': 'high',
        'signals': [
            {'kind': 'unauthorized_network_call', 'snippet': 'import urllib; urllib.urlopen("http://malicious.com")'}
        ]
    }
    
    if use_ai:
        print("Running AI analysis with gemma4:12b via Ollama...")
        result = explain(sample_finding)
        print("\n" + result)
    else:
        print("AI Explainer not requested. Run with --explain to get LLM insights.")
    
    return 0


def _handle_check():
    """Handle the check command."""
    
    if len(sys.argv) < 4:
        print('Usage: python3 -m checker check NAME VERSION [--explain]')
        return 1
    
    name = sys.argv[2]
    version = sys.argv[3]

    use_ai = '--explain' in sys.argv[2:]
    
    print(f"Checking package '{name}' version '{version}' (AI Explainer enabled: {use_ai})...\n")
    
    return 0


if __name__ == "__main__":
    main()