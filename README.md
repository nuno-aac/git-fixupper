# git-fixupper
This repository includes a python script to automate fixing up files to commits.

## Script dependencies
The following package dependecies must be installed before using this script.

- `termcolor`

## Usage

When the script is run in a git folder it prints to the console all the modified files in the repository grouped by the last commit they were present in. 

### `--fixup` flag

If the `--fixup` flag is passed to the script the user will be prompted to confirm if the commits should be fixed up automatically.

### Example

` > python3 fixupper.py --fixup`
