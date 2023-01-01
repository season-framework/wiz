VERSION=$1
python setup.py bdist_wheel
twine upload dist/season-$VERSION-py3-none-any.whl 