# UncertaintyAndBankProfits
  The repository contains the code I wrote for my Senior Thesis at Singapore Management University, "Banking on Banks: Impact of Interest Rates and Uncertainty on Bank Profits." Repository contains code files which:
 1. Extract publically available US Call reports data from the Chicago Fed's website inside the Data folder. Only publically available data and reasonably sized data (Full call report df was 80 GB) is uploaded.
 2. Clean and process the data into a useable format.
 3. Analyses the data to produce the tables and figures I include in the paper.

		|Data - contains jupyter notebooks used to download and combine US Call Reports into a long panel
		|______	FedRates - interest-rate and term premia time series of various horizons retrieved from FRED
		|______	MacroControls - macroeconomic time series retrieved from FRED
		|______	MacroFinanceUncertainty_202308Update - macroeconomic uncertainty indicators developed by Jurado et al (2015), retrieved from their website
		|Writing - contains all writing related outputs from the code; currently only tables
		|______	tables - regression tables optimized for input to LaTeX
		|x13as - seasonal adjustment library downloaded from census.gov to be used with Python
		|customFunctions.r - custom functions written for convenience in data processing and analysis
		|Data_* - data processing pipeline. Important to follow in order unless you are sure you know what you are doing
		|IR Regressions_* - descriptive statistics, figures, and regressions for the paper

## Questions the paper will answer
1. What is the impact of interest rates and macroeconomic and interest-rate uncertainty on bank profits?
2. What is the transmission mechanism behind the aforementioned impact?
3. Is the impact amplified for financially constrained firms?
