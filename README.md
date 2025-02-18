# sf-fish-completion

This repository contains a script to generate fish completion for the Salesforce CLI.

The salesforce cli does not support fish itself, this script generates the bash completion code and converts it for fish. Some extra functionality has been added to autocomplete usernames and test classes.

For the usernames and testclass completion to work the [`jq`](https://stedolan.github.io/jq/), [`fd`](https://github.com/sharkdp/fd) and [`rg`](https://github.com/BurntSushi/ripgrep) commands have to be available.

## Installation

In most cases running `install.fish` should be sufficient. This will generate the bash completion file and install it in `~/.config/fish/completions/sf.fish`.

The `generate-completion.py` script can be run manually to write the completion script to stdout. This can then be redirected to a file to install it.
The script accepts an optional `--add-descriptions` flag to add descriptions to the completions. This will run `sf <subcommand> --help` for each subcommand and use the first line of the help text as the description. Generating the descriptions will take a lot longer as it has to spawn a new process to run the help command.
Other parameters to `generate-completion.py` are interpreted as files to process, if no files are provided `~/.cache/sf/autocomplete/functions/bash/sf.bash` will be used.


## License

Copyright (C) 2025  Hans Alves

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
