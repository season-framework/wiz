import importlib.util
import os
from setuptools import setup, find_packages

SRC_DIR = 'src'
SEASON_PKG_DIR = os.path.join(SRC_DIR, 'season')
spec = importlib.util.spec_from_file_location('version', os.path.join(SEASON_PKG_DIR, 'version.py'))
version = importlib.util.module_from_spec(spec)
spec.loader.exec_module(version)

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join(path, filename)[len(SEASON_PKG_DIR) + 1:])
    return paths

extra_files = package_files(os.path.join(SEASON_PKG_DIR, 'command'))
extra_files = extra_files + package_files(os.path.join(SEASON_PKG_DIR, 'data'))
extra_files = extra_files + package_files(os.path.join(SEASON_PKG_DIR, 'framework')) 
extra_files = extra_files + package_files(os.path.join(SEASON_PKG_DIR, 'util')) 
extra_files = extra_files + package_files(os.path.join(SEASON_PKG_DIR, 'websrc'))
extra_files = extra_files + package_files(os.path.join(SEASON_PKG_DIR, 'wiz'))

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
    package_dir={'': SRC_DIR},
    packages=find_packages(SRC_DIR),
    include_package_data=True,
    package_data = {
        'season': extra_files
    },
    zip_safe=False,
    entry_points={'console_scripts': [
        'sf = season.cmd:main [season]',
        'wiz = season.cmd_wiz:main [season]'
    ]},
    install_requires=[
        'werkzeug==2.0.3',
        'jinja2==3.0.3',
        'flask',
        'watchdog',
        'argh',
        'psutil',
        'pypugjs',
        'lesscpy',
        'libsass',
        'dukpy',
        'flask_socketio',
        'GitPython'
    ],
    python_requires='>=3.6',
    classifiers=[
        'License :: OSI Approved :: MIT License'
    ] 
)