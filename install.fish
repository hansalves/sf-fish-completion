#!/usr/bin/env fish
sf autocomplete script bash
mkdir -p ~/.config/fish/completions/
./generate-completion.py (bash -c 'eval $(sf autocomplete script bash); echo $SF_AC_BASH_COMPFUNC_PATH') > ~/.config/fish/completions/sf.fish
