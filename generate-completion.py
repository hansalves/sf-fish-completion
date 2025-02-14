#!/usr/bin/env python3

import os
import sys
import subprocess


class Command:
    def __init__(self, name):
        self.name = name
        self.subcommands = {}
        self.options = []

root_commands = Command('sf')

def get_description(cmd):
    full_cmd = cmd + ['--help']
    return subprocess.check_output(full_cmd, text=True).split('\n')[0]

def add_command(command, command_parts):
    first = command_parts[0]
    if first not in command.subcommands:
        command.subcommands[first] = Command(first)
    if len(command_parts) > 1:
        return add_command(command.subcommands[first], command_parts[1:])
    else:
        return command.subcommands[first]

def generate_completion(command, stack):
    condition = f'''-n "__sf_is_subcommand {' '.join(stack + [command.name])}"'''
    if len(command.subcommands) > 0:
        subcommands = ' '.join(command.subcommands.keys())
        print(f"complete -c sf {condition} -f -a '{subcommands}'")
        for subcommand in command.subcommands.values():
            generate_completion(subcommand, stack + [command.name])
    if len(command.options) > 0:
        for option in command.options:
            if option == '--target-org':
                print(f"complete -c sf {condition} -s o -l {option.lstrip('-')} -f -ra '(__sf_usernames)'")
            elif option == '--test-level':
                print(f"complete -c sf {condition} -s l -l {option.lstrip('-')} -f -ra 'NoTestRun RunSpecifiedTests RunLocalTests RunAllTestsInOrg'")
            elif option == '--tests':
                print(f"complete -c sf {condition} -s t -l {option.lstrip('-')} -f -ra '(__sf_testclasses)'")
            elif option == '--api-version':
                print(f"complete -c sf {condition} -s a -l {option.lstrip('-')} -f -r")
            elif option == '--wait':
                print(f"complete -c sf {condition} -s w -l {option.lstrip('-')} -f -r")
            elif option == '--source-dir':
                print(f"complete -c sf {condition} -s d -l {option.lstrip('-')} -r")
            elif option == '--metadata':
                print(f"complete -c sf {condition} -s m -l {option.lstrip('-')} -f -r")
            else:
                print(f"complete -c sf {condition} -l {option.lstrip('-')}")

def main(infile):
    with open(os.path.join(os.path.dirname(__file__), infile)) as f:
        commands_found = False
        for line in f:
            if not commands_found:
                if line.strip() == 'local commands="':
                    commands_found = True
                continue
            if line.strip() == '"':
                commands_found = False
                break
            line = line.strip()
            if line:
                parts = line.split(' ')
                command = parts[0]
                command_parts = parts[0].split(':')
                cmd = add_command(root_commands, command_parts)
                for option in parts[1:]:
                    cmd.options.append(option)
    print('''
function __sf_usernames
	if test -d ~/.sfdx
		ls ~/.sfdx/ | grep '@' | sed -e 's/.json$//g'
	end
	if test -f ~/.sfdx/alias.json  && command -v jq >/dev/null 2>&1
		jq '.orgs | keys[]' -r ~/.sfdx/alias.json
	end
end

function __sf_testclasses
	if command -v fd >/dev/null 2>&1 && command -v rg >/dev/null 2>&1
		fd -g '*.cls' -0 | xargs -0 rg --ignore-case --multiline --replace '$5' --only-matching --no-line-number --no-filename '@istest\n((global|public|private)\s+)?((with|without)\s+sharing\s+)?class\s+(\w+)'
	end
end

function __sf_is_subcommand
	set -l cmd (commandline -poc)
	set -l cmd_len (count $cmd)
	set -l argv_len (count $argv)
	if test $cmd_len -lt $argv_len
		return 1
	end
	for i in (seq 1 $argv_len)
		if test $cmd[$i] != $argv[$i]
			return 1
		end
	end
	if test $argv_len -lt $cmd_len
		# the first argument after $argv should be an option, not another subcommand
		return (test (string sub --length 1 -- $cmd[(math $argv_len + 1)]) = '-')
	end
	return 0
end
''')
    generate_completion(root_commands, [])

if __name__ == '__main__':
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            main(arg)
    else:
        main(os.path.expanduser('~/.cache/sf/autocomplete/functions/bash/sf.bash'))
