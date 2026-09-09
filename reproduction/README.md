# Reproduction notes and validation

The [main README](../README.md) introduces the paper and gives the commands to
prepare data and generate tables and figures. This folder collects the detailed
run notes, source and input provenance, numerical comparisons, and validation
tools. Commands and code-formatted paths below are relative to the repository
root; paths stored in the JSON manifests and benchmarks are also repository-relative.

The target is the [April 2024 thesis](../Writing/UncertaintyAndBankProfits.pdf),
compiled on 14 April 2024. Page numbers below count the cover as page 1.

## Current status

The completed build yields 432,159 filtered bank-quarter observations against
427,375 in the PDF. The main analysis stops at this sample check. A separate
28-model diagnostic run quantifies the differences, but exact reproduction
remains unresolved. The preparation scripts currently stop raw reports at
2023 Q2; the original conversion source includes all of 2023. Restoring that
preparation window and rerunning the pipeline is the next empirical step.
See [result differences](RESULT_COMPARISON.md) for the evidence and interpretation.

| File or directory | Contents |
| --- | --- |
| [VALIDATION.md](VALIDATION.md) | Supplied-input checks, sample comparisons, and build status |
| [RESULT_COMPARISON.md](RESULT_COMPARISON.md) | Differences from the paper, interpretation, and possible error sources |
| [source_provenance.json](source_provenance.json) | Source revisions and SHA-256 fingerprints |
| [data_provenance.json](data_provenance.json) | Input vintages, coverage, derived files, and X13 engine details |
| [raw_input_manifest.json](raw_input_manifest.json) | Raw Call Report file identities |
| [reproduction_chunks.json](reproduction_chunks.json) | R analysis chunks and their corresponding results |
| [check_reproduction.py](check_reproduction.py) | Source, input-availability, and selected numerical checks |
| [reference/](reference/) | PDF benchmarks and saved table and figure assets |
| [tests/](tests/) | Benchmark-reader, merger-mapping, and seasonal-reporting tests |

Generated reports and diagnostic drivers remain under `outputs/input_validation/`
and `outputs/sensitivity/`, excluded from Git alongside other generated outputs.

## Results and benchmarks

| Result | PDF page | Code | Table or figure filename |
| --- | --- | --- | --- |
| Table 1: descriptive statistics | 9 | `reproduce.Rmd`: `filter-panel`, `table-1` | `descStats.csv` |
| Figure 1: uncertainty series | 20 | `macro-data`; `figures.ipynb` | `uncertainPlots.png` |
| Table 2: NIM, NNI, ROA | 21 | `table-2` | `bankProfitsMUReg.txt` |
| Table 3: channels | 22 | `table-3` | `explanatoryReg.txt` |
| Table 4: NIM interactions | 23 | `table-4-*` | `didRegNIM.txt` |
| Table 5: NNI interactions | 24 | `table-5-*` | `didRegNNI.txt` |
| Figure 2: bivariate plots | 25 | `figures.ipynb` | `biVariatePlots.png` |
| Tables 6–8: variable definitions | 27–33 | PDF data appendix; `Data_3-VariableCreation.ipynb` | Definitions, not estimated tables |
| Table 9: NIM subsamples | 35 | `subsample-groups`, `table-9` | `bankProfitsMURegSubsample.txt` |
| Table 10: NNI subsamples | 36 | `table-10` | `NNIMURegSubsample.txt` |

Tables are written to `outputs/paper/tables/`, figures to
`outputs/paper/figures/`, and the merged figure panel to
`outputs/paper/figure_panel.csv`. The analysis also writes R session information.

`reproduction/reference/paper_targets.json` records benchmarks transcribed from the PDF:
observations, the first coefficient row and its standard errors, R-squared, and
within R-squared for Tables 2–5 and 9–10. All 210 numeric cells in
`reproduction/reference/tables/descStats.csv` match Table 1. Table snapshots for Tables 3, 5,
and 10 supply additional reference material; their selected benchmark rows
are checked by the validator. They are not proof of a new estimation run.

The RGB pixels of both `reproduction/reference/figures/` images match the corresponding
images embedded in the PDF exactly. This establishes the reference assets'
identity; it does not establish that running the plotting code reproduces them.

## Data preparation

**Adjustment-window finding:** the current scripts and completed build truncate
raw reports at 2023 Q2. The April 2024 conversion source includes all of 2023;
applying the regression endpoint before seasonal adjustment changes the input
history. A controlled December-window test changes X13 eligibility for 13 of
16 tested banks. The full original-window rerun is outstanding; see
[RESULT_COMPARISON.md](RESULT_COMPARISON.md). The steps below describe the
currently implemented June-window build, not a verified reproduction.

Run the two notebooks inside `Data/` with `Data/` as the working directory.
Run all numbered processing files from the repository root, in numerical order.

1. **Quarterly and annual reports.** `Data/code_downloadCallReports.ipynb`
   converts Chicago Fed XPT files for 1976–2010 and FFIEC bulk ZIP files for
   2001–2023 into annual CSVs. Chicago Fed XPT files belong in
   `Data/ChicagoFedCallReportsLegacy/quarterly/`; annual CSVs belong one directory
   above. FFIEC ZIPs belong in `Data/ChicagoFedCallReports/zips/`. The paper's
   endpoint is 2023 Q2; the FFIEC conversion excludes subsequent quarters.
   The acquisition cells use interactive browser selectors and a Windows Edge
   driver path that must be configured for the execution environment. Existing
   annual extracts can be used without running acquisition cells.
2. **Field selection.** `Data/code_createCombinedDatasets.ipynb` selects 107
   balance-sheet fields and 64 income-statement fields, plus bank identifiers,
   and writes `Data/legacyCallReports(73-10).csv` and
   `Data/newCallReports(01-23).csv`. Its MDRM dictionary export uses
   `Data/MDRM/MDRM_CSV.csv` and writes `Data/finalData/finalVarDict.csv`.
3. **Combined panel.** `Data_1-CombineCallReports.r` uses Chicago Fed observations
   through 2010 and FFIEC observations from 2011 through 2023 Q2. It creates
   `Data/finalData/` and writes `findf_AllSeries.csv`.
4. **Merger adjustment.** `Data_2-MergerAdjust.ipynb` removes bank holding
   companies and maps predecessors to surviving banks as of December 1, 2023.
   Balance-sheet and income-statement values are divided equally among acquirers
   and summed at the acquirer-quarter level, following Appendix A. The notebook
   prepares `transformations.csv` from the source records, excludes transformations
   after December 1, 2023 and codes 5 and 7, and stops on circular mappings.
   Required files under `Data/MergerAdjust/` are:

   | Input | Purpose | Availability |
   | --- | --- | --- |
   | `CSV_ATTRIBUTES_ACTIVE.csv` | Active institution attributes | Supplied; records through September 2026 |
   | `CSV_ATTRIBUTES_CLOSED.csv` | Closed institution attributes | Supplied; records through July 2026 |
   | `CSV_ATTRIBUTES_BRANCHES.csv` | Branch attributes | Supplied; records through September 2026 |
   | `transformations.csv` | Prepared ultimate-successor mapping | Generated; 60,532 rows through December 1, 2023 |
   | `CSV_TRANSFORMATIONS.CSV` | Transformation history for preparing the mapping | Supplied; records through September 4, 2026 |

5. **Bank variables.** `Data_3-VariableCreation.ipynb` constructs durations,
   shares, profit rates, controls, and income components. It writes
   `findf_RelSeries.csv` and `Data/bankTreasuryHoldings.csv`.
6. **Contiguity and seasonal adjustment.** `Data_4-ContiguousTimeSeries.r`
   selects contiguous series and writes `findf_RelSeriesContiguous.csv`.
   `Data_5-SeasonalAdjust.py` applies X13 to profit rates, asset growth, and
   income components, writing `findf_RelSeriesContiguousSA.csv`. It expects an
   appropriate X13 executable under `x13as/`. Failed seasonal adjustments are
   represented by missing values; rows missing the six main adjusted series
   are excluded. Failure details are written to
   `outputs/paper/seasonal_adjustment_failures.csv`; a missing executable or an
   empty surviving panel stops execution. Inspect failures and resulting
   coverage before estimation. Processing defaults to one worker; set
   `THESIS_X13_WORKERS=4` to adjust four banks concurrently. Concurrent execution
   preserves bank order and uses a separate temporary directory for each fit.

The analysis requires both `Data/finalData/findf_RelSeriesContiguousSA.csv` and
`Data/bankTreasuryHoldings.csv`; these must be generated by the numbered stages. The supplied
`Data/findf_RelSeries_CSA_MacroSeries.csv` is a different processed panel and does
not replace these inputs (see `reproduction/VALIDATION.md`). Raw Chicago Fed
annual CSVs, FFIEC ZIPs, and MDRM records are locally available but excluded from
Git. Their presence does not establish the precise vintage used in the paper.
Use period-appropriate inputs: later bank attributes or revised histories can
alter both the sample and seasonal adjustment.

Small interest-rate and macroeconomic inputs come from the April 2024 source
revision, except `Data/MacroControls/spyVix.csv`, whose 2024 vintage has not been
verified. The uncertainty workbook is the August 2023 release. Standardization
uses the full workbook before quarterly aggregation, so substituting a newer
workbook can change values even within the same analysis window.

## Specification and sample checks

The final panel is restricted to 1997 Q2–2023 Q2. The analysis requires 427,375
observations for Table 1 and 420,772 for each main regression in Table 2.
Other table counts and numerical benchmarks are in `reproduction/reference/paper_targets.json`.

The regressions use bank fixed effects, the lagged dependent variable, bank and
macro controls, and Driscoll–Kraay covariance with four lags. The interest-rate
specification separates the expected-rate component from the Kim–Wright term
premium. Table 4 estimates the NIM version of Equation (2); Table 5 uses NNI.
Subsamples use within-quarter maturity-gap and asset-size terciles, and the
indicator for zero interest-rate derivatives.

Rate volatility is the within-quarter standard deviation of daily DGS3MO after
complete-case merging DGS2, DGS3MO, DGS5, DGS10, and T10Y3M. Macroeconomic
uncertainty uses the standardized 12-month-horizon series and quarterly means.
Figures use the exported analysis panel and quarterly means of bank outcomes.

Two implementation details matter when interpreting the written methodology:
`winsOutliers` clips at the pooled 1st and 99th percentiles, although the paper
calls this trimming; and the 24-observation eligibility check counts rows,
while contiguous-series selection is a separate upstream step. These are the
implemented rules used by this pipeline.

## Software and validation

Python processing uses pandas, NumPy, tqdm, statsmodels, SciPy, matplotlib,
openpyxl, and a Jupyter kernel. Acquisition also uses Selenium. R uses fixest,
tsibble, tidyverse, moments, lubridate, knitr, xtable, bimets, and seasonal.
X13 is an external executable. There is no verified 2024 dependency lockfile.
The local validation environment combines compatible installed packages with
packages built under `.r-library/`; its versions and library paths are recorded
with the run outputs. This is not a verified 2024 package environment.

```sh
# File integrity, Python syntax, and available reference-table benchmarks
python3 reproduction/check_reproduction.py --source-only
python3 -m unittest discover -s reproduction/tests -v

# The same checks, plus required analysis-input availability
python3 reproduction/check_reproduction.py

# After estimation: displayed Table 1 and selected regression benchmarks
python3 reproduction/check_reproduction.py --results
```

The validator uses the Python standard library. It compares displayed numeric
values, including scientific notation, exactly after parsing; it does not apply
an arbitrary tolerance to unrounded estimates. Table 1 checks include its labels
and row/column order. Regression checks cover 140 numeric entries across all six
estimated regression tables, including all 28 model sample sizes. The supplied
Table 3, 5, and 10 snapshots cover 75 of these benchmark entries.

Full verification additionally requires comparing the remaining coefficients,
standard errors, significance stars, and generated figures, inspecting the
upstream sample and seasonal-adjustment failures, and recording input vintages
and software versions. Source integrity and benchmark agreement alone cannot
establish an end-to-end numerical reproduction.

Input checks and empirical comparisons for the supplied files are recorded in
`reproduction/VALIDATION.md` and `reproduction/data_provenance.json`. Generated audit details are under
`outputs/input_validation/`.
