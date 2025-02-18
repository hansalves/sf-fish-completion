#!/usr/bin/env fish

# Generate the bash completion code
sf autocomplete script bash

# Create the fish completions directory if it doesn't exist
mkdir -p ~/.config/fish/completions/

# Generate the fish completion file
./generate-completion.py (bash -c 'eval $(sf autocomplete script bash); echo $SF_AC_BASH_COMPFUNC_PATH') > ~/.config/fish/completions/sf.fish
