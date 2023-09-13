# https://pylint.pycqa.org/en/latest/pyreverse.html

pyreverse \
--output png \
--max-color-depth 3 \
--colorized  \
--ignore __init__.py,logging.py,exceptions.py,connection.py,helpers.py,propertyelement.py,utils.py,import_scripts,shared.py,set_encoder.py \
--output-directory docs/assets/pyreverse \
src/dsp_tools
