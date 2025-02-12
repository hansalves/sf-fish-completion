#!/usr/bin/env python3

import os
import sys
import subprocess


class Command:
    def __init__(self, name):
        self.name = name
        self.subcommands = {}


root_commands = Command('sf')

def get_description(cmd):
    full_cmd = cmd + ['--help']
    #print(full_cmd, file=sys.stderr)
    return subprocess.check_output(full_cmd, text=True).split('\n')[0]

def add_command(command, command_parts):
    first = command_parts[0]
    if first not in command.subcommands:
        command.subcommands[first] = Command(first)
    if len(command_parts) > 1:
        add_command(command.subcommands[first], command_parts[1:])

def print_command(command, stack):
    #print(''.join('  ' for _ in stack), command.name, '--', stack, file=sys.stderr)
    print(' '.join(stack + [command.name]), '--', get_description(stack + [command.name]))
    for subcommand in command.subcommands.values():
        print_command(subcommand, stack + [command.name])

def generate_completion(command, stack):
    subcommands = ' '.join(command.subcommands.keys())
    #print(f"set -l sf_{'root' if len(stack) == 0 else '_'.join(stack)}_commands {subcommands}")
    condition = f'''-n "__sf_is_subcommand {' '.join(stack + [command.name])}"'''
    print(f"complete -c sf {condition} -f -a '{subcommands}'")
    for subcommand in command.subcommands.values():
        #generate_completion(subcommand, stack + [command.name])
        if len(subcommand.subcommands) > 0:
            generate_completion(subcommand, stack + [command.name])

with open(os.path.join(os.path.dirname(__file__), 'sf-commands.txt')) as f:
    for line in f:
        line = line.strip()
        if line:
            parts = line.split(' ')
            command = parts[0]
            command_parts = parts[0].split(':')
            add_command(root_commands, command_parts)

print('''
function __sf_is_subcommand
    set -l cmd (commandline -poc)
    set -l cmd_len (count $cmd)
    set -l argv_len (count $argv)
    if test $cmd_len -ne $argv_len
        return 1
    end
    for i in (seq 1 (count $cmd))
        if test $cmd[$i] != $argv[$i]
            return 1
        end
    end
    return 0
end
''')

#print_command(root_commands, [])
generate_completion(root_commands, [])