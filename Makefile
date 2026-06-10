PYTHON ?= python

.PHONY: all reproduce validate tables figures test clean

all: reproduce

## reproduce: regenerate Table 5, Table 5a, and the BaTiO3 soft-mode figure
reproduce: validate tables figures

## validate: fit BaTiO3 + SrTiO3 linewidths and check against published Table 5
validate:
	$(PYTHON) scripts/validate_bto_linewidths.py
	$(PYTHON) scripts/validate_sto_literature.py

## tables: write tables/table5.{md,csv} and tables/table5a.{md,csv}
tables:
	$(PYTHON) scripts/make_tables.py

## figures: write figures/fig_bto_soft_mode.png and fig_bto_linewidth_fit.png
figures:
	$(PYTHON) scripts/make_figures.py

## test: regression test that the CSVs reproduce the published Table 5
test:
	$(PYTHON) -m pytest -q tests/

## clean: remove regenerated outputs (raw data is never touched)
clean:
	rm -f data/processed/*.csv tables/table5*.csv tables/table5*.md figures/fig_bto_*.png
	rm -rf scripts/__pycache__ tests/__pycache__ .pytest_cache
