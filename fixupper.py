# Script dependencies
import argparse
import subprocess
import re
from termcolor import colored

# Parse the command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--fixup', action='store_true', help='Create fixup commits for the modified files')
args = parser.parse_args()

# Current branch name
branch_name = subprocess.run(['git', 'branch', '--show-current'], capture_output=True).stdout.decode().strip()

# Function for parsing commits into a (hash, message) shape
def parse_commit(commit):
  commit_regex = re.search(r'([a-z0-9]{6,9}) - (?:\(.*\) )?(.*) \(.*\).*$', commit)

  if commit_regex:
    return commit_regex.group(1,2)

  return None

# Function for parsing commits into a (hash, branches, message) shape
def parse_commit_list(commit):
  commit_regex = re.search(r'([a-z0-9]{6,9}) - (\(.*\))?(.*) \(.*\).*$', commit)

  if commit_regex:
    return commit_regex.group(1,2,3)

  return None

def get_branch():
  # Log command for last 100 commits
  log_format_config = r"'format:%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset'"
  log_command = 'git log --pretty={} -100'.format(log_format_config)

  log_output = subprocess.run(log_command, capture_output=True, shell=True).stdout

  # Get commits between this branch and previous one
  commits = []
  for commit in log_output.decode().split('\n'):
    (hash, branches, message) = parse_commit_list(commit)

    if(branches and not branch_name in branches):
      break;
      
    commits.append((hash, message))

  return commits


# Run `git status` and capture the output then split the output into a list of files
output = subprocess.run(['git', 'status', '-s'], capture_output=True).stdout
files = list(map(lambda file: file.strip().split(), output.decode().split('\n')))[:-1]

commits_in_branch = get_branch()
start_hash = '{}~1'.format(commits_in_branch[-1][0])
end_hash = commits_in_branch[0][0]

# Create a dictionary to store the modified files for each commit
modified_files = {}

# Iterate over the list of files
for file in files:
  file_path = file[1]
  file_name = ' '.join(file[1:])
  file_status = file[0]

  # Command to log all commits from current branch that include the file
  log_format_config = r"'format:%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset'"
  log_command = 'git log --pretty={log_format} {start_hash}..{end_hash} --follow -- {file_path}'.format(start_hash=start_hash, end_hash=end_hash, file_path=file_path, log_format=log_format_config)

  # Run the previous command for the file and capture the output
  log_output = subprocess.run(log_command, capture_output=True, shell=True).stdout

  # Split the log output into a list of commits in the shape of (hash, message)
  commits = list(map(parse_commit, log_output.decode().split('\n')))

  # Set the defaults in case file is not yet present in the branch
  latest_commit_hash = 'no-hash'
  latest_commit_message = ''

  if commits and commits[0]:
    # Get the latest commit hash where the modified file appears
    latest_commit_hash, latest_commit_message = commits[0]

  # Add the modified file to the list of modified files for the latest commit
  modified_files.setdefault(latest_commit_hash, {
    "commit_message": latest_commit_message,
    "files": []
  })["files"].append({
    "path": file_path,
    "status": file_status
  })

#
# OUTPUT
# 

def status_colors(status):
  colors = {
    'A': 'green',
    'D': 'red',
    'M': 'yellow',
    '??': 'blue',
    'R': 'cyan'
  }
  if status in colors:
    return colors[status]
  return 'white'

fixup_errors = []

print(colored('''
               _                         
  _  o _|_   _|_ o         _   _   _  ._ 
 (_| |  |_    |  | >< |_| |_) |_) (/_ |  
  _!                      |   |           
''', attrs=['bold']))


# Print the currently modified files grouped by commit
for commit_hash, commit in modified_files.items():
  if commit_hash != 'no-hash':
    print(colored(commit_hash, 'green', attrs=['bold']), '-', commit['commit_message'])
    for file in commit['files']:
      print(colored(' {} >'.format(file['status'][0]), status_colors(file['status'])), colored(file['path'], 'grey'))

if 'no-hash' in modified_files:
    print(colored('no-hash', 'red', attrs=['bold']), '-', 'These files have not yet been commited in this branch, they will be ignored in fixup mode.')
    for file in modified_files['no-hash']['files']:
      print(colored(' {} >'.format(file['status'][0]), status_colors(file['status'])), colored(file['path'], 'grey'))

# Check if user wants to proceed with fixup
if(args.fixup):
  allowFixup = input('\nProceed to fixup? (y/n) ').upper()   

# If the `--fixup` flag was provided, the user allowed and there are modified files
if args.fixup and allowFixup == 'Y' and modified_files:
  # Iterate over the dictionary of modified files, if there is an hash fix them up to that commit
  for commit_hash, commit in modified_files.items():
    if commit_hash != 'no-hash':
      file_list = [file['path'] for file in commit['files']]
      # Stage the modified files
      subprocess.run(['git', 'add'] + file_list)

      # Create the fixup commit
      fixup_output = subprocess.run(['git', 'commit', '--fixup', commit_hash])

      # If the fixup command fails unstage the changes and warn the user at the end 
      if fixup_output.returncode == 1:
        fixup_errors.append(commit_hash)
        subprocess.run(['git', 'reset'], capture_output=True)

  # Warn the user in case any fixup fails
  if len(fixup_errors) > 0:
    print(colored('\nERROR > ', 'red'), "There was an error when running git fixup in the following commits:")
    for commit in fixup_errors:
      print(colored('      > ', 'red'), commit)

  # Warn the user in case some files are not handled by the script
  if 'no-hash' in modified_files:
    print(colored('\nINFO  > ', 'cyan'), "The following files were ignored for not being commited in this branch yet:")
    for file in modified_files['no-hash']['files']:
      print(colored('      > ', 'cyan'), file['path'])
