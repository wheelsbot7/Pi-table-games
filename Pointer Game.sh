#!/bin/sh
printf '\033c\033]0;%s\a' Pointer Game
base_path="$(dirname "$(realpath "$0")")"
"$base_path/Pointer Game.arm64" "$@"
