library(tidyverse)
library(tsibble)
source("customFunctions.r")

df = read.csv("./Data/finalData/findf_RelSeries.csv") %>%
  mutate(RSSD9999 = yearquarter(RSSD9999)) %>%
  as_tsibble(key = RSSD9001, index = RSSD9999) %>%
  arrange(RSSD9999, RSSD9001)

# Filter longest contiguous time series
pb_Contiguous = progress_estimated(length(unique(df$RSSD9001))*(ncol(df) - 2))
df = df %>%
  fill_gaps() %>%
  group_by_key() %>%
  mutate(across(.cols = IEA:last_col(),.fns = function(x) longestContiguousTS(x, RSSD9999, pb_Contiguous))) %>%
  ungroup() %>%
  drop_na()

print(dim(df))
write.csv(df, "./Data/finalData/findf_RelSeriesContiguous.csv")