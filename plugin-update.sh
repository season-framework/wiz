VERSION=$1

sh /opt/github/wiz/plugin-commit.sh core $VERSION
sh /opt/github/wiz/plugin-commit.sh utility $VERSION
sh /opt/github/wiz/plugin-commit.sh workspace $VERSION
sh /opt/github/wiz/plugin-commit.sh git $VERSION