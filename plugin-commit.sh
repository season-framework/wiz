PLUGIN=$1
VERSION=$2

mv /opt/github/wiz-plugin/$PLUGIN/.git /opt/github/wiz-plugin/.git
rm -rf /opt/github/wiz-plugin/$PLUGIN/
cp -R /opt/github/wiz/src/season/data/plugin/$PLUGIN /opt/github/wiz-plugin/$PLUGIN
cp /opt/github/wiz/src/season/data/plugin/$PLUGIN/.gitignore /opt/github/wiz-plugin/$PLUGIN/.gitignore
mv /opt/github/wiz-plugin/.git /opt/github/wiz-plugin/$PLUGIN/.git
cd /opt/github/wiz-plugin/$PLUGIN
git add -A .
git commit -m "$VERSION"
git push

cd /opt/github/wiz