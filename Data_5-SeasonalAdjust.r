library(tidyverse)
library(tsibble)
source("customFunctions.r")

df = read.csv("./Data/finalData/findf_RelSeriesContiguous.csv") %>%
  mutate(RSSD9999 = yearquarter(RSSD9999)) %>%
  as_tsibble(key = RSSD9001, index = RSSD9999) %>%
  arrange(RSSD9999, RSSD9001)

# Seasonally adjust using X11
pb_Season = progress_estimated(length(unique(df$RSSD9001))*7)
df = df %>%
  as_tsibble(key = RSSD9001, index = RSSD9999) %>%
  group_by_key() %>%
  mutate(across(.cols = c(intExpenseRateAnn, intIncomeRateAnn, niiRateAnn, nniRateAnn, niiLoansRateAnn, roaAnn, deltaLogA), 
                .fns = function(x) getSeasonallyAdjustedSeries(x, RSSD9999, pb_Season),
                .names = "{.col}SeasAdj")) %>%
  drop_na(c(intExpenseRateAnnSeasAdj, intIncomeRateAnnSeasAdj, niiRateAnnSeasAdj, nniRateAnnSeasAdj, niiLoansRateAnnSeasAdj, roaAnnSeasAdj, deltaLogASeasAdj)) %>%
  ungroup()

print(dim(df))
write.csv(df, "./Data/finalData/findf_RelSeriesContiguousSA.csv")
