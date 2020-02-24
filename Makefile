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
	make -C SystemCode/Fulfillment/ run

run_ngrok:
	make -C SystemCode/Fulfillment/ run_ngrok

rasa_train:
	make -C SystemCode/rasa/ rasa_train_nlu

rasa_test:
	make -C SystemCode/rasa/ rasa_test_nlu


rasa_run:
	make -C SystemCode/rasa/ rasa_run


