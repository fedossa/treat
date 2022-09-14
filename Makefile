L?=R

# Set to R or python above(no space) or call make with L=R or L=python argument.
# If you are new to Makefiles: https://makefiletutorial.com

PAPER := output/paper.pdf

PRESENTATION := output/presentation.pdf

TARGETS :=  $(PAPER) $(PRESENTATION)

EXTERNAL_DATA := data/external/fama_french_12_industries.csv \
	data/external/fama_french_48_industries.csv

ifeq ($L, R)
	CLI:=Rscript --encoding=UTF-8
	SCRIPT_EXT:=R
	DATA_EXT:=rds
	RESULT_EXT:=rda
	DOC_EXT:=Rmd
	render_doc_fn = $(CLI) -e 'library(rmarkdown); render("${1}.$(DOC_EXT)")'
else ifeq ($L,python)
	CLI:=python
	SCRIPT_EXT:=py
	DATA_EXT:=csv
	RESULT_EXT:=json
	DOC_EXT:=qmd
	render_doc_fn = quarto render $(1).$(DOC_EXT) --quiet
else
$(error Langauge(L) has to be R or python, also please make sure that there are no trailing white space.)
endif

WRDS_DATA := data/pulled/cstat_us_sample.$(DATA_EXT)

GENERATED_DATA := data/generated/acc_sample.$(DATA_EXT)

RESULTS := output/results.$(RESULT_EXT)

.phony: all, clean very-clean dist-clean

all: $(TARGETS)

clean:
	rm -f $(TARGETS)
	rm -f $(RESULTS)
	rm -f $(GENERATED_DATA)
	
very-clean: clean
	rm -f $(WRDS_DATA)

dist-clean: very-clean
	rm config.csv
	
config.csv:
	@echo "To start, you need to copy _config.csv to config.csv and edit it"
	@false
	
$(WRDS_DATA): code/$L/pull_wrds_data.$(SCRIPT_EXT) code/$L/read_config.$(SCRIPT_EXT) \
	config.csv
	$(CLI) code/$L/pull_wrds_data.$(SCRIPT_EXT)

$(GENERATED_DATA): $(WRDS_DATA) $(EXTERNAL_DATA) code/$L/prepare_data.$(SCRIPT_EXT)
	$(CLI) code/$L/prepare_data.$(SCRIPT_EXT)

$(RESULTS):	$(GENERATED_DATA) code/$L/do_analysis.$(SCRIPT_EXT)
	$(CLI) code/$L/do_analysis.$(SCRIPT_EXT)

$(PAPER): doc/paper.$(DOC_EXT) doc/references.bib $(RESULTS)
	$(call render_doc_fn,doc/paper)
	mv doc/paper.pdf output
	rm -f doc/paper.ttt doc/paper.fff
	
$(PRESENTATION): doc/presentation.$(DOC_EXT) $(RESULTS) \
doc/beamer_theme_trr266.sty
	$(call render_doc_fn,doc/presentation)
	mv doc/presentation.pdf output