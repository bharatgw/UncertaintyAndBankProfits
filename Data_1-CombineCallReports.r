library(tidyverse)
library(tsibble)

legacyCallReports = read.csv("./Data/legacyCallReports(73-10).csv")
newCallReports = read.csv("./Data/newCallReports(01-23).csv")

# Join split legacy and new Call Reports; Observations after 2010Q4 are from the new call reports
newCallReports = newCallReports %>%
  rename(RSSD9001 = IDRSSD, RSSD9999 = RCON9999) %>%
  filter(RSSD9999 >= 20110000)

callReports = legacyCallReports %>%
  bind_rows(newCallReports)

rm(legacyCallReports, newCallReports)

findf = callReports %>%
  mutate(RSSD9999 = as.Date(as.character(RSSD9999), format = "%Y%m%d")) %>%
  tsibble(key = RSSD9001, index = RSSD9999)

rm(callReports)

# Write the joined unedited call reports dataset
print(dim(findf))
write.csv(findf, "./Data/finalData/findf_AllSeries.csv")