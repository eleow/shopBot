.PHONY: clean run migrate refresh

TEST_PATH=./

help:
	@echo ""


rasa_train_nlu:
	rasa train nlu -c config.yml --nlu data/nlu_train --fixed-model-name nlu_rasa

rasa_test_nlu:
	rasa test nlu -m models/nlu_rasa.tar.gz --nlu data/nlu_test

rasa_run:
	rasa run --enable-api -m models/nlu_rasa.tar.gz --cors "*"
