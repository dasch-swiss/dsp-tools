# https://pylint.pycqa.org/en/latest/pyreverse.html

pyreverse \
-o png \
--max-color-depth 3 \
--colorized  \
--ignore logging.py,exceptions.py,connection.py,helpers.py,propertyelement.py,utils.py,import_script.py,shared.py,set_encoder.py \
--output-directory docs/assets/pyreverse \
src/dsp_tools
