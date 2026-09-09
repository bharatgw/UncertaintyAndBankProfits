# The Impact of Interest Rates and Uncertainty on Bank Profits

Code and data preparation for [Bharat Gangwani's April 2024 senior thesis](Writing/UncertaintyAndBankProfits.pdf)
at Singapore Management University, supervised by Associate Professor Anthony Tay.

The paper studies how the yield curve, macroeconomic uncertainty, and
interest-rate volatility relate to US bank profitability. It uses quarterly
Call Reports from 1997 Q2 to 2023 Q2: 427,375 bank-quarter observations in the
descriptive sample and 420,772 in each main profitability regression. The
models include bank fixed effects, lagged profitability, bank and macroeconomic
controls, and Driscoll–Kraay standard errors with four lags.

## Key results from the paper

The following are the **published estimates**. NIM denotes net interest margin;
NNI denotes net non-interest income, and ROA denotes return on assets.

| Finding | Published estimate | Location |
| --- | --- | --- |
| Macroeconomic uncertainty is negatively associated with NIM at the model's baseline. | −19 basis points per unit of the standardized uncertainty index; significant at 5%. | Table 2 |
| The baseline short-rate coefficient for NIM is negative. | −9 basis points per percentage-point increase in the three-month Treasury yield; significant at 1%. | Table 2 |
| The treasury-share result is consistent with banks reallocating assets toward Treasuries during greater uncertainty. | Uncertainty coefficient of +4.14 percentage points; significant at 5%. The uncertainty coefficients for the other proposed channels are not significant. | Table 3 |
| Larger banks have a less negative baseline NIM response to macroeconomic uncertainty. | Large-minus-small-bank uncertainty coefficient of +17 basis points; significant at 5%. | Table 4 |
| Banks without interest-rate derivatives have a more negative NIM response to interest-rate volatility. | Non-user-minus-user volatility coefficient of −3 basis points per volatility unit; significant at 5%. | Table 4 |

The standalone macroeconomic-uncertainty coefficients for NNI and ROA are not
statistically significant in Table 2. Neither are the interest-rate-volatility
coefficients for any of the three main profitability outcomes.

The paper's headline long-run calculation is an approximately **70-basis-point
NIM decline for a one-standard-deviation increase in uncertainty**, compared
with **34 basis points for a one-percentage-point rise in the short rate**.
These calculations use the standalone coefficients and lagged NIM coefficient.
The models contain interest-rate squares and uncertainty interactions, so the
reported magnitudes are conditional baseline calculations; responses vary with
the yield curve and uncertainty. They should not be read as sample-average
causal effects.

## Generate the tables and figures

### 1. Set up the software

Use R and Python with the following packages. The Jupyter kernel must use the
Python environment containing the processing packages.

| Runtime | Packages |
| --- | --- |
| R | `fixest`, `tsibble`, `tidyverse`, `moments`, `lubridate`, `knitr`, `xtable`, `bimets`, `seasonal` |
| Python | `pandas`, `numpy`, `tqdm`, `statsmodels`, `scipy`, `matplotlib`, `openpyxl`, `jupyter` |
| Data acquisition only | Python `selenium` and a configured browser driver |
| Seasonal adjustment | An executable X13-ARIMA-SEATS binary for your platform under `x13as/` |

### 2. Prepare the bank data

Small macroeconomic inputs are included in `Data/`. Large bank datasets are
local inputs excluded from Git. Place the Chicago Fed reports, FFIEC bulk
reports, MDRM dictionary, and institution attribute/transformation files in the
locations listed in the [data preparation guide](reproduction/README.md#data-preparation).

First run `Data/code_downloadCallReports.ipynb` to obtain or convert annual
extracts, then `Data/code_createCombinedDatasets.ipynb` to select the reporting
fields. Both notebooks use **`Data/` as their working directory**. Acquisition
is interactive and requires browser configuration; if annual extracts are
already available, start with the field-selection notebook.

Then run the numbered stages from the **repository root**, proceeding only
after each stage succeeds:

```sh
mkdir -p outputs/preparation
Rscript Data_1-CombineCallReports.r
jupyter nbconvert --to notebook --execute Data_2-MergerAdjust.ipynb --ExecutePreprocessor.timeout=-1 --output Data_2-MergerAdjust.executed.ipynb --output-dir outputs/preparation
jupyter nbconvert --to notebook --execute Data_3-VariableCreation.ipynb --ExecutePreprocessor.timeout=-1 --output Data_3-VariableCreation.executed.ipynb --output-dir outputs/preparation
Rscript Data_4-ContiguousTimeSeries.r
THESIS_X13_WORKERS=4 python3 Data_5-SeasonalAdjust.py
```

These stages join reports, adjust mergers, construct bank variables, select
contiguous series, and seasonally adjust. X13 can take several hours; omit
`THESIS_X13_WORKERS=4` to use the default single worker.

If the two analysis inputs below are already prepared, begin with estimation:

- `Data/finalData/findf_RelSeriesContiguousSA.csv`
- `Data/bankTreasuryHoldings.csv`

### 3. Estimate and plot

Run from the repository root:

```sh
Rscript -e 'dir.create("outputs/paper", recursive=TRUE, showWarnings=FALSE); knitr::knit("reproduce.Rmd", output="outputs/paper/reproduce.md")'
jupyter nbconvert --to notebook --execute figures.ipynb --ExecutePreprocessor.timeout=-1 --output figures.executed.ipynb --output-dir outputs/paper
```

Run the figure notebook after estimation succeeds. Generated files are:

| Output | Contents |
| --- | --- |
| `outputs/paper/tables/` | Table 1, Tables 2–5, and appendix Tables 9–10 |
| `outputs/paper/figures/` | Figures 1–2 |
| `outputs/paper/figure_panel.csv` | Shared input panel for the figures |
| `outputs/paper/reproduce.md` | Executed R analysis |
| `outputs/paper/R-sessionInfo.txt` | R session and package versions |

Tables 6–8 are variable definitions in the paper's data appendix.

## Repository layout

| Path | Purpose |
| --- | --- |
| `Writing/UncertaintyAndBankProfits.pdf` | April 2024 thesis |
| `Data/` | Macroeconomic inputs, bank-data acquisition and field selection |
| `Data_1-*` through `Data_5-*` | Bank-panel preparation |
| `customFunctions.r` | Filtering and time-series routines |
| `reproduce.Rmd` | Tables and figure-panel export |
| `figures.ipynb` | Figures |
| `reproduction/` | Run notes, provenance, comparisons, checks, and reference results |
| `outputs/` | Generated files, excluded from Git |
