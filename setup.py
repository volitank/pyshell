# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from pathlib import Path
import pyshell
# Define the directory that setup.py is in
here = Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name=pyshell.__title__,  # Required
    version=pyshell.__version__,  # Required
    description='A Linux subprocess module.',  # Optional
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional (see note above)
    url='https://github.com/volitank/pyshell',  # Optional
    author=pyshell.__author__,  # Optional
    author_email='blake@volitank.com',  # Optional
    classifiers=[  # Optional
	# List of classifiers https://gist.github.com/nazrulworld/3800c84e28dc464b2b30cec8bc1287fc
        'Development Status :: 1 - Planning',
		'Environment :: Console',
		'Intended Audience :: System Administrators',
		'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
		'Natural Language :: English',
		'Operating System :: POSIX :: Linux',
		'Topic :: System :: Operating System Kernels :: Linux',
		'Topic :: System :: Systems Administration',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
    ],

    keywords='python, shell, subprocess',  # Optional
    packages=['pyshell'],  # Required
    python_requires='>=3.6, <4',

    project_urls={  # Optional
        'Documentation': 'https://volitank.com/pyshell',
        'Source': 'https://github.com/volitank/pyshell',
    },
)