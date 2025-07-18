#!/usr/bin/env python3

import os
import sys
import subprocess
import argparse

class Command:
    def __init__(self, name):
        self.name = name
        self.subcommands = {}
        self.options = []

def get_description(cmd):
    full_cmd = cmd + ['--help']
    proc = subprocess.run(full_cmd, text=True, stdout=subprocess.PIPE, input="")
    if proc.returncode != 0:
        return ''
    return proc.stdout.split('\n')[0]


def add_command(command, command_parts):
    first = command_parts[0]
    if first not in command.subcommands:
        command.subcommands[first] = Command(first)
    if len(command_parts) > 1:
        return add_command(command.subcommands[first], command_parts[1:])
    else:
        return command.subcommands[first]


def generate_completion(command, stack, add_descriptions=False):
    condition = f'''-n "__sf_is_subcommand {' '.join(stack + [command.name])}"'''
    if len(command.subcommands) > 0:
        if not add_descriptions:
            subcommands = ' '.join(command.subcommands.keys())
            print(f"complete -c sf {condition} -f -a '{subcommands}'")
        for subcommand in command.subcommands.values():
            if add_descriptions:
                description = get_description(stack + [command.name, subcommand.name])
                if description:
                    description = description.replace("'", r"\'")
                    print(f"complete -c sf {condition} -f -a '{subcommand.name}' -d '{description}'")
                else:
                    print(f"complete -c sf {condition} -f -a '{subcommand.name}'")
            generate_completion(subcommand, stack + [command.name], add_descriptions)
    if len(command.options) > 0:
        for option in command.options:
            if option == '--api-version':
                print(f"complete -c sf {condition} -s a -l api-version -f -r")
            elif option == '--file':
                print(f"complete -c sf {condition} -s f -l file -r -F")
            elif option == '--flags-dir':
                print(f"complete -c sf {condition} -l flags-dir -r -a '(__fish_complete_directories)'")
            elif option == '--metadata':
                print(f"complete -c sf {condition} -s m -l metadata -f -r")
            elif option == '--source-dir':
                print(f"complete -c sf {condition} -s d -l source-dir -r -F")
            elif option == '--target-org':
                print(f"complete -c sf {condition} -s o -l target-org -f -ra '(__sf_usernames)'")
            elif option == '--test-level':
                print(f"complete -c sf {condition} -s l -l test-level -f -ra 'NoTestRun RunSpecifiedTests RunLocalTests RunAllTestsInOrg'")
            elif option == '--tests':
                print(f"complete -c sf {condition} -s t -l tests -f -ra '(__sf_testclasses)'")
            elif option == '--wait':
                print(f"complete -c sf {condition} -s w -l wait -f -r")
            elif "file" in option:
                print(f"complete -c sf {condition} -l {option.lstrip('-')} -r -F")
            else:
                print(f"complete -c sf {condition} -l {option.lstrip('-')}")

def main():
    parser = argparse.ArgumentParser(
        prog='generate-completion',
        description='Generate fish completion for sf')
    parser.add_argument('-d', '--add-descriptions', action='store_true', help='Add descriptions to the subcommands')
    parser.add_argument('files', action='store', help='Files to process, defaults to ~/.cache/sf/autocomplete/functions/bash/sf.bash', nargs='*')
    args = parser.parse_args()
    if len(args.files) > 1:
        for arg in args.files:
            generate_for_file(arg, args.add_descriptions)
    else:
        generate_for_file(os.path.expanduser('~/.cache/sf/autocomplete/functions/bash/sf.bash'), args.add_descriptions)

def generate_for_file(infile, add_descriptions):
    root_commands = Command('sf')
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
		fd -g '*.cls' -0 | xargs -0 rg --ignore-case --multiline --replace '$5' --only-matching --no-line-number --no-filename '@istest\n((global|public|private)\\s+)?((with|without)\s+sharing\s+)?class\\s+(\\w+)'
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
    generate_completion(root_commands, [], add_descriptions)

if __name__ == '__main__':
    main()
