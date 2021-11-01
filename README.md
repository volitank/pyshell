# pyshell
A Linux subprocess module, An easier way to interact with the Linux shell
>pyshell should be cross platform but has only been tested with linux

# Installation

You can install a specific release by running

`$ pip install https://github.com/volitank/pyshell/releases/download/v1.0.0a2/pyshell-1.0.0a2.tar.gz`

While we're still in early development stages it is preferred that you run directly from the git

`$ pip install https://github.com/volitank/pyshell/archive/refs/heads/main.tar.gz`

# Usage

    from pyshell import pyshell
    shell = pyshell()
    shell.echo('Hello', "GitHub!")
    
# Docs

Check out the Official [Documentation](https://volitank.com/pyshell/index.html) for help with syntax and different arguments
