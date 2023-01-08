VERSION=$1

find /opt/github/wiz/src | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf

sh /opt/github/wiz/plugin-commit.sh core $VERSION
sh /opt/github/wiz/plugin-commit.sh utility $VERSION
sh /opt/github/wiz/plugin-commit.sh workspace $VERSION
sh /opt/github/wiz/plugin-commit.sh git $VERSION
sh /opt/github/wiz/plugin-commit.sh portal $VERSION