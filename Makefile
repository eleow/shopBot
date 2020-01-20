.PHONY: clean run migrate refresh

TEST_PATH=./

help:
	@echo "    run"
	@echo "    	   run system 


clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f  {} +
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf docs/_build

run:
	make -C SystemCode/ run

