# Generate UML diagrams of the dsp_tools package
################################################

# This script generates 2 UML diagrams of the dsp_tools package:
# "package.png" shows the interconnections between the modules,
# "classes.png" shows the interconnections between the classes.

# Requirements: pylint, graphviz
# See https://pylint.pycqa.org/en/latest/pyreverse.html

# Usage: 
# $ chmod u+x docs/assets/pyreverse/pyreverse.sh
# $ ./docs/assets/pyreverse/pyreverse.sh
# If "--only-classnames" is used, the attributes and methods of the classes are omitted.

pyreverse \
--ignore import_scripts,logging.py,shared.py,utils.py,model.py,exceptions.py,connection.py,helpers.py,propertyelement.py,set_encoder.py \
--only-classnames \
--output-directory docs/assets/pyreverse \
--max-color-depth 3 \
--colorized  \
--output dot \
src/dsp_tools
