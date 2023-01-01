VERSION=$1
rm -rf dist
rm -rf build
python setup.py bdist_wheel
twine upload dist/season-$VERSION-py3-none-any.whl 