# Web Font Generator

This package is intended for generating web fonts from SVG icon set

## Requirements

following packages should be installed (with `apt-get install`):

* python (>= 2.6)
* python-fontforge
* python-rsvg
* python-yaml

```sh
sudo apt-get install -y python python-fontforge python-rsvg python-yaml
```

to make eot files you should compile google [ttf2eot](https://code.google.com/p/ttf2eot/) utility. [Download it](https://ttf2eot.googlecode.com/files/ttf2eot-0.0.2-2.tar.gz) and install with following commands (this commands tested on ubuntu trusty):

```sh
cd /tmp
wget https://ttf2eot.googlecode.com/files/ttf2eot-0.0.2-2.tar.gz
# for latest version retrieve it from svn repo:
#svn checkout http://ttf2eot.googlecode.com/svn/trunk/ ttf2eot
tar -zxf ttf2eot-0.0.2-2.tar.gz
cd ttf2eot-0.0.2-2/
sed -i 's/.*#include <string\.h>.*/#include <stddef.h>\n&/' OpenTypeUtilities.cpp
make
cp ttf2eot /path/to/webfont
chmod +x /path/to/webfont/ttf2eot
chmod +x /path/to/webfont/webfont.py
```

## Usage

The table below describes command-line options or config variables. Command-line options overrides config variables.

config var|option|description|default value
----------|------|-----------|-------------
work-dir|--work-dir -d|project root folder|config directory
output-dir|--output-dir -o|output folder relative to work-dir|work-dir itself
icons-dir|--icons-dir -i|icons folder relative to work-dir|icons
debug|--debug -D|print some debug info|`False`
default-extensions|--default-extensions -e|comma separated list of default extensions|`'svg font css'`
font-copyright|--font-copyright -l|`'OFL'`
font-family|--font-family -n|font family|camel-cased work-dir
font-weight|--font-weight -w|font weight|`500`
font-formats|--font-formats -f|comma separated output formats. Valid values are: `all`, `otf`, `ttf`, `eot`, `woff`, `svg`, `sfd` |`'all'`
font-output|--font-output -F|fonts output folder (except .sfd) relative to output-dir|output-dir itself
sfd-output|--sfd-output -S|SFD font file output folder relative to work-dir|work-dir itself

To specify config file location use `--config=/path/to/config` option. If config file is not specified `.webfont.yml` will be searched in current folder and in user home.

Relative work-dir path will be expanded with config directory. Relative icon-dir will be expanded with work-dir.
