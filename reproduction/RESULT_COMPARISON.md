# Result differences and their interpretation

The current rebuild gives very similar reported regression coefficients, with
some changes near significance thresholds. It is not an exact reproduction.
A confirmed difference from the April 2024 source is the June 2023 cutoff applied
**before** seasonal adjustment. The diagnostic estimates below use that truncated
build and must be revisited after restoring the original preparation window.

The checks were run on September 9, 2026 against
`Writing/UncertaintyAndBankProfits.pdf`. All 28 specifications in Tables 2–5 and
9–10 were estimated using the existing `reproduce.Rmd` chunks and the saved
432,159-row filtered panel. The diagnostic driver skips the expected-PDF sample
assertions and redirects output to `outputs/sensitivity/`; the assertions in
`reproduce.Rmd` remain unchanged. Both figures were also generated separately.
These outputs are diagnostics, not replacements for the paper's results.

## How large are the differences?

| Quantity | PDF | Current rebuild | Difference |
| --- | ---: | ---: | ---: |
| Table 1 observations | 427,375 | 432,159 | +4,784 (+1.119%) |
| Table 2 observations, each model | 420,772 | 425,487 | +4,715 (+1.121%) |
| Mean assets | 710,117.12 | 710,444.91 | +0.046% |
| Mean equity | 69,238.38 | 69,409.40 | +0.247% |
| Mean maturity gap, years | 4.12 | 4.13 | +0.01 |
| Mean loan share | 62.79% | 62.77% | −0.02 percentage points |
| Mean treasury share | 16.06% | 16.07% | +0.01 percentage points |
| Mean NIM | 0.98% | 0.98% | Same displayed value |
| Mean NNI | −0.60% | −0.60% | Same displayed value |
| Mean ROA | 0.26% | 0.26% | Same displayed value |

Only 76 of Table 1's 210 cells match exactly at displayed precision, but an exact
match count is not a measure of economic distance. The means above illustrate
how small differences can fail exact checks. The complete cell comparisons are
in `outputs/sensitivity/descriptive_differences.csv`. Across the regression
specifications, observation counts are 0.88%–1.42% above the PDF's counts.

For 435 reported coefficient cells in Tables 2–5 and 9–10:

- 433 retain their sign. Both sign changes concern insignificant coefficients.
- 427 retain the same decision at a 5% significance threshold.
- 423 retain the same star category at the 10%, 5%, and 1% thresholds.
- 205 round to the PDF's displayed coefficient.

These counts include repeated full-sample estimates in the appendix; they are
not 435 independent tests. The comparison covers all reported coefficient rows
in Tables 2, 4, 5, 9, and 10, plus 18 complete rows in Table 3. Eleven values in
Table 3's partially populated rows are outside this comparison. The original
unrounded PDF estimates and p-values are unavailable: differences are measured
against printed coefficients and significance against printed stars. Coarse
rounding can account for much of an apparent coefficient difference.

The median absolute coefficient difference is 0.038 of its printed standard
error. After allowing for the rounding interval of each printed coefficient,
the largest remaining discrepancy is about 0.34 printed standard errors.
These are measures of numerical distance, not statistical tests of equality
between estimates from overlapping samples. A total of 480 extracted PDF
coefficient/standard-error values also agree with independent reference table
files; all six regression-table pages were visually inspected.

## Do the findings change?

The central *reported coefficient* findings survive in this diagnostic build.
The following comparisons use the paper's standalone coefficients; interaction
terms make their interpretation conditional, as discussed below. Basis points
refer to the dependent-variable rate/share, and an uncertainty change is one
unit of the standardized index.

| Reported coefficient | PDF | Rebuild | Rebuild p-value |
| --- | ---: | ---: | ---: |
| Table 2: uncertainty coefficient for NIM, basis points | −19 | −18.71 | 0.0179 |
| Table 2: short-rate coefficient for NIM, basis points per percentage point | −9 | −9.46 | 0.00231 |
| Table 3: uncertainty coefficient for treasury share, percentage points | +4.14 | +4.137 | 0.0473 |
| Table 4: large-minus-small-bank NIM uncertainty coefficient, basis points | +17 | +16.65 | 0.0221 |
| Table 4: non-user-minus-user NIM interest-rate-volatility coefficient, basis points per volatility unit | −3 | −3.18 | 0.0353 |

The standalone uncertainty coefficients remain insignificant for NNI and ROA,
with p-values 0.728 and 0.340. The loan-share, loan-provision, and maturity-gap
uncertainty coefficients remain insignificant; the treasury-share result is
positive but close to the 5% boundary. The large-bank NIM protection result and
the negative volatility difference for derivative non-users also remain.

The main lag coefficients change from 0.7266, 0.5295, and 0.4387 to 0.727407,
0.529003, and 0.438850. Table 2 R-squared changes by at most 0.00038, and within
R-squared by at most 0.00087. The paper's baseline long-run NIM calculation
becomes −68.64 basis points for uncertainty and −34.71 for the short rate,
compared with its text's approximately −70 and −34. Their ratio is 1.978:
“roughly twice” remains apt for this calculation; “more than twice” does not
hold literally in the current diagnostic estimates.

Examples of threshold changes:

- Table 2's NIM term-premium coefficient moves from one star to two
  (p = 0.0496).
- Table 2's NNI squared expected-slope coefficient moves from one star to two
  (p = 0.0490).
- Table 2's ROA expected-slope coefficient moves from three stars to two
  (p = 0.0102).
- Table 3's short-rate × lagged-loan-share coefficient in the loan-provision
  equation moves from two stars to one (p = 0.0510).

The full list is in `outputs/sensitivity/pdf_coefficient_comparison.csv`.

Figure 2 retains all four fitted-line directions. Its macro-uncertainty/NIM
R-squared is 0.10492, which prints as 0.10 rather than the paper's 0.11; the
other three R-squared values still print as 0.02, 0.00, and 0.16. The macro-
uncertainty/NNI intercept prints as −0.0060 rather than −0.0061. These are small
plot-summary differences; pixel-for-pixel figure reproduction is not claimed.

### An interpretation issue distinct from reproduction

The NIM specification interacts uncertainty with the short rate, expected
slope, term premium, and their squares. Consequently its contemporaneous
uncertainty slope is

```
beta_U + beta_yU*y + beta_sU*s + beta_pU*p
       + beta_y2U*y^2 + beta_s2U*s^2 + beta_p2U*p^2,
```

where `y` is DGS3MO, `s` is AER10−DGS3MO, and `p` is TP10. The standalone
−18.71-basis-point coefficient sets these three rate components to zero. It is
not the average slope at the rates observed in the sample.

Using the complete interaction expression, the bank-quarter-weighted average
contemporaneous slope in the current estimation sample is **−0.387 basis
points**, with a Driscoll–Kraay standard error of **0.249 basis points** and
**p = 0.124** (103 degrees of freedom). The average holds observed regressors
fixed. The implied quarterly slopes range from −5.69 to +1.83 basis points;
about 44.1% of estimation observations have a negative implied slope. The
calculation was independently checked against the estimator's design matrix;
maximum disagreement was below 6e-19 in dependent-variable units.

Thus stable standalone coefficients do not establish the paper's broad
unconditional effect-size interpretation. Its roughly 70-basis-point long-run
number is a baseline-coefficient calculation, whereas the −0.387 number above
is an average contemporaneous slope: they are different quantities and horizons.
The comparison at a common contemporaneous horizon is −18.71 versus −0.387.
This is an interpretation issue inherent in the interacted specification, not
evidence that the additional 1.1% of observations overturned an old average
effect. The original unrounded estimates are needed to calculate the paper's
original average slope accurately. These calculations also do not establish
causal identification of uncertainty shocks.

## Sources of discrepancy

1. **Confirmed: the preprocessing endpoint differs from the original code.**
   `Data_1-CombineCallReports.r:10` and the acquisition/conversion filters in
   `Data/code_downloadCallReports.ipynb` truncate at June 30, 2023. The April
   2024 conversion source includes all quarters of 2023 and its combination
   script has no June cutoff. The regression endpoint and the seasonal-fitting
   endpoint should not be conflated. Additional observations can revise earlier
   seasonal adjustments, as described in the [Census seasonal-adjustment
   guidance](https://www.census.gov/data/software/x13as/seasonal-adjustment-questions-answers.html).

   A controlled test rebuilt the extra two quarters for the 16 supplied banks
   excluded by required-series X13 failures. Every shared pre-cutoff input value
   in the tested failed series was exactly unchanged; all 16 failures were
   reproduced using the June window. Extending to December made all six required
   adjustments succeed for **13 of the 16 banks**. These banks account for
   **1,226 of the supplied panel's 1,380 rows absent after the June-window X13
   step**. This establishes an effect on eligibility, not their final inclusion
   after the remaining filters or the exact full-sample effect of a December
   rebuild. One remaining failure is an all-zero expense series, one a singular
   regression, and one a growth-series convergence failure. The supplied panel
   therefore cannot serve as unquestioned evidence of the original pipeline.

2. **Input vintage and preparation remain uncertain.** The supplied institution
   records extend into 2026. Restricting transformation dates does not reverse
   historical revisions or restore old institution classifications. The supplied
   May 2024 processed panel itself differs from the PDF and lacks adjusted asset
   growth. It is a useful diagnostic comparison, not a verified 2024 benchmark.

3. **Seasonal failures affect samples and downstream filters.** The current full
   build has 41,878 failed bank-series fits. Most are in ancillary income
   components; 284 banks fail at least one required series. Growth filtering,
   the 24-observation rule, pooled winsorization, lags, and quarterly terciles can
   transmit changes in eligibility to other observations and regression samples.
   The window test identifies one concrete cause of those changes.

4. **Software differences can affect close significance decisions.** The run
   uses R 4.6.1, fixest 0.13.2, and a macOS build of X13 1.1 Build 60. The X13
   version matches the identifier in the historical Windows executable, but the
   compiler/platform and complete 2024 package environment are not locked.
   Current fits report covariance-matrix repairs; fixest documents this behavior
   in its [HAC covariance reference](https://lrberge.github.io/fixest/reference/vcov_hac.html).
   Data and runtime contributions have not been fully separated. A star moving
   around p = 0.05 should not be treated as a reversal of the economic mechanism.

Two checks narrow the search: all 13 checked macro variables match the supplied
panel across 105 quarters to floating-point precision, and ten unadjusted bank
variables match away from winsorized endpoints. Serial/concurrent X13 checks
also agree exactly. These checks do not prove historical vintage equivalence,
but make a broad macro-data or concurrency error less plausible.

For common bank-quarters away from the supplied panel's winsorized endpoints,
mean absolute differences between its adjustments and the June-window rebuild
are 0.0076 basis points for NIM, 0.0089 for NNI, and 0.0203 for ROA. The respective
99th percentiles are 0.185, 0.141, and 0.357 basis points. A few differences are
much larger: maxima are 11.15, 39.17, and 66.00 basis points. These are comparisons
with the supplied processed file, not the unavailable original estimation panel.

The next reproduction step is a full build using the original through-2023
preparation window, followed by the unchanged 1997 Q2–2023 Q2 analysis restriction
and PDF checks. Current diagnostic estimates quantify sensitivity to the
existing build; they do not substitute for that rerun.

Machine-readable results and drivers are under `outputs/sensitivity/`, including
`run_provenance.json`, `coefficients.csv`, `model_statistic_comparison.csv`,
`pdf_coefficient_comparison.csv`, `nim_effect_checks.json`,
`seasonal_value_differences.csv`, `window_x13_comparison.csv`, and
`window_all_main_fits.csv`.
