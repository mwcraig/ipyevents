from os import path

from jupyter_packaging import (
    create_cmdclass, install_npm, ensure_targets,
    combine_commands, ensure_python,
    get_version, skip_if_exists
)

from setuptools import setup, find_packages

LONG_DESCRIPTION = 'A custom widget for returning mouse and keyboard events to Python'

HERE = path.dirname(path.abspath(__file__))

# The name of the project
name = 'ipyevents'

# Ensure a valid python version
ensure_python('>=3.6')

# Get our version
version = get_version(path.join(name, '_version.py'))

nb_path = path.join(HERE, name, 'nbextension', 'static')
lab_path = path.join(HERE, name, 'labextension')

# Representative files that should exist after a successful build
jstargets = [
    path.join(nb_path, 'index.js'),
    path.join(lab_path, 'package.json'),
]

package_data_spec = {
    name: [
        'nbextension/static/*.*js*',
        'labextension/**'
    ]
}

data_files_spec = [
    ('share/jupyter/nbextensions/ipyevents',
        nb_path, '*.js*'),
    ('share/jupyter/labextensions/ipyevents', lab_path, '**'),
    ('etc/jupyter/nbconfig/notebook.d', HERE, 'ipyevents.json')
]


cmdclass = create_cmdclass('jsdeps', package_data_spec=package_data_spec,
                           data_files_spec=data_files_spec)
js_command = combine_commands(
    install_npm(HERE, build_cmd='build'),
    ensure_targets(jstargets),
)

is_repo = path.exists(path.join(HERE, '.git'))
if is_repo:
    cmdclass['jsdeps'] = js_command
else:
    cmdclass['jsdeps'] = skip_if_exists(jstargets, js_command)

setup_args = dict(
    name            = name,
    description     = 'A custom widget for returning mouse and keyboard events to Python',
    version         = version,
    cmdclass        = cmdclass,
    packages        = find_packages(),
    author          = 'Matt Craig',
    author_email    = 'mattwcraig@gmail.com',
    url             = 'https://github.com/mwcraig/ipyevents',
    license         = 'BSD 3-clause',
    platforms       = "Linux, Mac OS X, Windows",
    keywords        = ['Jupyter', 'Widgets', 'IPython'],
    classifiers     = [
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Framework :: Jupyter',
    ],
    include_package_data = True,
    install_requires = [
        'ipywidgets>=7.6.0',
    ],
    extras_require = {
        'test': [
            'pytest',
            'pytest-cov',
            'nbval',
        ],
        'docs': [
            'sphinx>=1.5',
            'recommonmark',
            'sphinx_rtd_theme',
            'nbsphinx>=0.2.13,<0.4.0',
            'jupyter_sphinx',
            'nbsphinx-link',
            'pytest_check_links',
            'pypandoc',
        ],
    },
)

if __name__ == "__main__":
    setup(**setup_args)
