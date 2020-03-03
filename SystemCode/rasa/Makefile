.PHONY: clean run migrate refresh

TEST_PATH=./
IMAGE=rasa/rasa:1.7.3-spacy-en
CURRENT_DIR=$(shell pwd)

help:
	@echo "    rasa_train_nlu"
	@echo "    	   train rasa nlu model on training dataset
	@echo "    rasa_test_nlu"
	@echo "    	   test rasa nlu model on test dataset
	@echo "    rasa_run"
	@echo "    	   run rasa nlu server locally on default port 5005
	@echo "    d_rasa_train_nlu"
	@echo "    	   train rasa nlu model on training dataset (using docker image $(IMAGE))
	@echo "    d_rasa_run"
	@echo "    	   run rasa nlu server (using docker image $(IMAGE)) on port 5015 (because default port 5005 is used by docker)


rasa_train_nlu:
	rasa train nlu -c config.yml --nlu data/nlu_train --fixed-model-name nlu_rasa

rasa_test_nlu:
	rasa test nlu -m models/nlu_rasa.tar.gz --nlu data/nlu_test

rasa_run:
	rasa run --enable-api -m models/nlu_rasa.tar.gz --cors "*"

d_rasa_train_nlu:
	docker run -v $(CURRENT_DIR):/app $(IMAGE) train nlu -c config.yml --nlu data/nlu_train --fixed-model-name nlu_rasa

d_rasa_run:
	docker run -p 5015:5015 -v $(CURRENT_DIR):/app $(IMAGE) run --enable-api -m models/nlu_rasa.tar.gz --cors "*" -p 5015

d_rasa_shell:
	docker run -it -v $(CURRENT_DIR):/app $(IMAGE) shell
