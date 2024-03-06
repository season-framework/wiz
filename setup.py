import importlib.util
import os
from setuptools import setup, find_packages

SRCPATH = os.path.join('src')
PKGPATH = os.path.join('src', 'season')
spec = importlib.util.spec_from_file_location('version', os.path.join(PKGPATH, 'version.py'))
version = importlib.util.module_from_spec(spec)
spec.loader.exec_module(version)

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join(path, filename)[len(PKGPATH) + 1:])
    return paths

extra_files = package_files(os.path.join(PKGPATH, "command"))
extra_files = extra_files + package_files(os.path.join(PKGPATH, "data"))
extra_files = extra_files + package_files(os.path.join(PKGPATH, "lib"))
extra_files = extra_files + package_files(os.path.join(PKGPATH, "util"))

setup(
    name='season',
    version=version.VERSION_STRING,
    description='season wiz web framework',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown', 
    url='https://github.com/season-framework/wiz',
    author='proin',
    author_email='proin@season.co.kr',
    license='MIT',
    package_dir={'': SRCPATH},
    packages=find_packages(SRCPATH),
    include_package_data=True,
    package_data = {
        'season': extra_files
    },
    zip_safe=False,
    entry_points={'console_scripts': [
        'wiz = season.cmd:main [season]'
    ]},
    install_requires=[
        'werkzeug==3.0.1',
        'jinja2==3.1.3',
        'texttable',
        'flask==3.0.2',
        'python-socketio==5.11.1',
        'flask-socketio==5.3.6',
        'argh',
        'psutil',
        'GitPython',
        'numpy',
        'pandas',
        'Pillow',
        'requests',
        'eventlet',
        'gevent',
        'natsort'
    ],
    python_requires='>=3.6',
    classifiers=[
        'License :: OSI Approved :: MIT License'
    ] 
)