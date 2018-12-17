venv: FORCE
	python3 -m venv ~/.venv/cloudmarker
	echo . ~/.venv/cloudmarker/bin/activate > venv

# In local development environment, we run `make venv` to create a
# `venv` script that can be used to activate the virtual Python
# environment conveniently by running `. ./venv`.
#
# However, Travis CI creates virtual Python environments on its own for
# each Python version found in the build matrix. Further, in certain
# production environments, we may not want to create virtual Python
# environments.
#
# In both of the above mentioned cases, we do not run `make venv`. But
# most of the commands below start with `. ./venv`, so a `venv` script
# is expected by all the commands. Therefore, we run `touch venv` to
# create an empty `venv` script if none exists. If `venv` already
# exists, then `touch venv` does nothing apart from altering its access
# and modification times.
deps: FORCE
	touch venv
	. ./venv && pip3 install -r requirements.txt
	. ./venv && pip3 install -r dev-requirements.txt

rmvenv: FORCE
	rm -rf ~/.venv/cloudmarker

test: FORCE
	. ./venv && python3 -m unittest discover -v

coverage: FORCE
	. ./venv && coverage run --source . --branch -m unittest discover -v
	. ./venv && coverage report --show-missing
	. ./venv && coverage html

# See pylama.ini for pylama configuration.
lint: FORCE
	. ./venv && pylama cloudmarker

checks: test coverage lint

clean: FORCE
	find . -name "__pycache__" -exec rm -r {} +
	find . -name "*.pyc" -exec rm {} +
	rm -rf .coverage htmlcov

FORCE:
