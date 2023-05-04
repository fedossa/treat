L ?= R

# Set to R or python above(no space) or call make with L=R or L=python argument.
# If you are new to Makefiles: https://makefiletutorial.com

PAPER := output/paper.pdf
PRESENTATION := output/presentation.pdf

TARGETS :=  $(PAPER) $(PRESENTATION)

ifeq ($(L),R)
	CLI := Rscript --encoding=UTF-8
	SCRIPT_EXT := R
	DATA_EXT := rds
	RESULT_EXT := rda
	DOC_EXT := Rmd
	render_doc_fn = $(CLI) -e 'library(rmarkdown); render("$<")'
else ifeq ($(L),python)
	CLI := python
	SCRIPT_EXT := py
	DATA_EXT := csv
	RESULT_EXT := pickle
	DOC_EXT := qmd
	render_doc_fn = quarto render $< --quiet 
else
$(error Language (L) must be R or python, and there should be no trailing white space.)
endif

# Configs
MAIN_CONF := conf/config.yaml
HYDRA_CONF := conf/hydra/job_logging/logging.yaml
SECRETS_CONF := conf/secrets/secrets.yaml
PULL_DATA_CONF := conf/pull_data/pull_data.yaml
PREPARE_DATA_CONF := conf/prepare_data/prepare_data.yaml
DO_ANALYSIS_CONF := conf/do_analysis/do_analysis.yaml

EXTERNAL_DATA := data/external/fama_french_12_industries.csv \
	data/external/fama_french_48_industries.csv

WRDS_DATA := data/pulled/cstat_us_sample.$(DATA_EXT)
GENERATED_DATA := data/generated/acc_sample.$(DATA_EXT)
RESULTS := output/results.$(RESULT_EXT)

.PHONY: all clean very-clean dist-clean

all: $(TARGETS)

clean:
	rm -f $(TARGETS) $(RESULTS) $(GENERATED_DATA)

very-clean: clean
	rm -f $(WRDS_DATA)

dist-clean: very-clean
	rm -f config.csv

$(WRDS_DATA): code/$(L)/pull_wrds_data.$(SCRIPT_EXT) $(MAIN_CONF) \
	$(HYDRA_CONF) $(SECRETS_CONF) $(PULL_WRDS_DATA_CONF) config.csv
	$(CLI) $<

$(GENERATED_DATA): code/$(L)/prepare_data.$(SCRIPT_EXT) $(WRDS_DATA) \
	$(EXTERNAL_DATA) $(PREPARE_DATA_CONF)
	$(CLI) $<

$(RESULTS): code/$(L)/do_analysis.$(SCRIPT_EXT) $(GENERATED_DATA) \
	$(DO_ANALYSIS_CONF)
	$(CLI) $<

$(PAPER): doc/paper.$(DOC_EXT) doc/references.bib $(RESULTS)
	$(call render_doc_fn,$<)
	mv doc/paper.pdf output
	rm -f doc/paper.ttt doc/paper.fff

$(PRESENTATION): doc/presentation.$(DOC_EXT) $(RESULTS) \
	doc/beamer_theme_trr266.sty
	$(call render_doc_fn,$<)
	mv doc/presentation.pdf output
	rm -rf doc/presentation_files