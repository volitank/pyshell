# pyshell
A Linux subprocess module, An easier way to interact with the Linux shell

# Installation

You can install the latest release

`$ pip install pyshell`

You can install directly from GitHub

`$ pip install https://github.com/volitank/pyshell/archive/refs/heads/main.tar.gz`

# Usage

    from pyshell import pyshell
    shell = pyshell()
    shell.echo('Hello', "GitHub!")
    
# Docs

Check out the Official [Documentation](https://volitank.com/pyshell/index.html) for help with syntax and different arguments

# TODO
- Update docs to include new expect and popen functionality.
- Update docs with new basic `import shell`
- Update docs with `DEFAULT, DEVNULL, PIPE, STDOUT` moving to `shell.`