# CYBERSEC ANALYZER

Scan a cloned repository and find spoiled (suspicious or tampered) packages.
Built for Hacktoberfest 2026 Hack Day Sonipat, Problem 4.

## The problem
Developers review source code on GitHub, but what actually runs is the
packages the project pulls in. Those can differ from their source, through
normal build steps or through tampering (for example the XZ backdoor,
CVE-2024-3094).

## What it does
- Takes the path of a locally cloned repository
- Finds the packages it depends on
- [Compares them against their source / checks them for suspicious signs - describe what yours does]
- Prints the spoiled packages in the terminal
- Writes an audit file with each finding and the reason

## Requirements
- Python [version]
- [Other tools, or "no third-party dependencies"]

## Install
git clone [repo link]
cd [repo name]
pip install -r requirements.txt

## Usage
python3 scan_repo.py <path-to-cloned-repo>

## Web interface
Open `[path/to/index.html]` in your browser [or: run `[command]` and open `[address]`].
1. Choose the cloned repository folder to scan.
2. Review the flagged packages and the reason for each.
3. Download the audit file.

The page runs in your browser and reads files from your own computer.

## Output
- Terminal: list of flagged packages
- Audit file: [file name and location], containing [package, version, reason, evidence]

## Example
See `examples/` for a sample input, the real terminal output and the audit file.

## Safety
The scanner only reads files. It never executes code from the repository
or from packages.

## Tests
pytest

## Limitations
[Honest list, e.g. supported ecosystems, what it cannot detect yet]

## Team
[names]

## License
MIT