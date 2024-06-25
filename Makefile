# If you are new to Makefiles: https://makefiletutorial.com

PAPER := output/paper.pdf
PRESENTATION := output/presentation.pdf

TARGETS :=  $(PAPER) $(PRESENTATION)

# Configs
PULL_DATA_CFG := config/pull_data_cfg.yaml
PREPARE_DATA_CFG := config/prepare_data_cfg.yaml
DO_ANALYSIS_CFG := config/do_analysis_cfg.yaml

EXTERNAL_DATA := data/external/fama_french_12_industries.csv \
	data/external/fama_french_48_industries.csv

WRDS_DATA := data/pulled/cstat_us_sample.csv
GENERATED_DATA := data/generated/acc_sample.csv
RESULTS := output/results.pickle

.PHONY: all clean very-clean dist-clean

all: $(TARGETS)

clean:
	rm -f $(TARGETS) $(RESULTS) $(GENERATED_DATA)

very-clean: clean
	rm -f $(WRDS_DATA)

dist-clean: very-clean
	rm -f config.csv

$(WRDS_DATA): code/python/pull_wrds_data.py $(PULL_DATA_CFG)
	python $<

$(GENERATED_DATA): code/python/prepare_data.py $(WRDS_DATA) \
	$(EXTERNAL_DATA) $(PREPARE_DATA_CFG)
	python $<

$(RESULTS): code/python/do_analysis.py $(GENERATED_DATA) \
	$(DO_ANALYSIS_CFG)
	python $<

$(PAPER): doc/paper.qmd doc/references.bib $(RESULTS)
	quarto render $< --quiet
	mv doc/paper.pdf output
	rm -f doc/paper.ttt doc/paper.fff

$(PRESENTATION): doc/presentation.qmd $(RESULTS) \
	doc/beamer_theme_trr266.sty
	quarto render $< --quiet
	mv doc/presentation.pdf output
	rm -rf doc/presentation_files