#!/bin/sh
# itefix installer for Linux
#   curl -fsSL https://raw.githubusercontent.com/TeaFaris/ite-upgrade-mode-fix/main/install.sh | sudo sh
set -eu
REPO="TeaFaris/ite-upgrade-mode-fix"

if [ "$(id -u)" -ne 0 ]; then
    echo "run it with sudo: curl -fsSL https://raw.githubusercontent.com/$REPO/main/install.sh | sudo sh"
    exit 1
fi
if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 is missing. Arch: pacman -S python, Debian/Ubuntu: apt install python3, Fedora: dnf install python3"
    exit 1
fi

tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT
curl -fsSL "https://raw.githubusercontent.com/$REPO/main/itefix.py" -o "$tmp"
python3 -c 'import ast, sys; ast.parse(open(sys.argv[1]).read())' "$tmp"
install -m 755 "$tmp" /usr/local/bin/itefix
echo "installed /usr/local/bin/itefix"
echo
itefix status || true
