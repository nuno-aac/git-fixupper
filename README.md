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

Modify the following alias with the correct path and add it to your gitconfig:

`fixupper = !sh -c 'python3 ~/Path/to/fixupper.py $1' -`

Example usage:

https://user-images.githubusercontent.com/34559473/219870175-875c3b5a-d7f4-47c7-96e1-661a50c7b3e3.mov

