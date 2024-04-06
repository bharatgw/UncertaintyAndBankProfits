library(tidyverse)
library(tsibble)

findf = read.csv("./Data/finalData/findf_AllSeries.csv")

gc()
# Create relevant variables
findf = findf %>%
  rowwise() %>%
  mutate(
    IEA = sum(RCON0071, RCON2122, RCON0390, RCON2146, RCON3545, RCON1754, RCON1772, RCON1350, RCONB987, RCONB989, na.rm = T),
    matAsset = sum(RCONA549, RCONA550, RCONA551, RCONA552, RCONA553, RCONA554, RCONA555, RCONA556, RCONA557, RCONA558, RCONA559, RCONA560, RCONA561, RCONA562, RCONA564, RCONA565, RCONA566, RCONA567, RCONA568, RCONA569, RCONA570, RCONA571, RCONA572, RCONA573, RCONA574, RCONA575, na.rm = T),
    savingDep = sum(RCON6810, RCON0352, na.rm = T),
    demandDep = RCON2215,
    timeDep = sum(RCON6648, RCON6645, RCON6646, RCON2604, RCONJ473, RCONJ474, na.rm = T),
  ) %>%
  mutate(
    matLiab = sum(RCONA579, RCONA580, RCONA581, RCONA582, RCONA584, RCONA585, RCONA586, RCONA587, RCONHK07, RCONHK08, RCONHK09, RCONHK10, RCONHK12, RCONHK13, RCONHK14, RCONHK15, RCONF055, RCONF056, RCONF057, RCONF058,  RCONF060, RCONF061, RCONF062, RCONF063, demandDep, savingDep, na.rm = T),
  ) %>%
  mutate(intExpenseRateAnn = sum(RIAD4073, -RIADC900, na.rm = T)/IEA * 4 * 100,
         intIncomeRateAnn = sum(RIAD4107, -RIADC899, -RIADB525, -RIAD4842, na.rm = T)/IEA * 4 * 100,
         niiRateAnn = sum(RIAD4074, -RIADC899, RIADC900, -RIADB525, -RIAD4842, na.rm = T)/IEA * 4 * 100,
         nniRateAnn = sum(RIAD4079, -RIAD4093, -RIADC902, -RIADC903, -RIADC904, -RIADC905, RIADC907, -RIAD4097, RIAD4239, na.rm = T)/IEA * 4 * 100,
         roaAnn = sum(RIAD4340, -RIADC914, -RIAD4341, na.rm = T)/IEA * 4 * 100,
         niiLoansRateAnn = sum(RIAD4107, -RIAD4115, -RIAD4020, -RIAD4073, na.rm = T)/IEA * 4 * 100,
         assetMatPeriod = sum(
           RCONA549 * 1.5,
           RCONA550 * 7.5,
           RCONA551 * 24,
           RCONA552 * 48,
           RCONA553 * 120,
           RCONA554 * 240,
           RCONA555 * 1.5,
           RCONA556 * 7.5,
           RCONA557 * 24,
           RCONA558 * 48,
           RCONA559 * 120,
           RCONA560 * 240,
           RCONA561 * 18,
           RCONA562 * 60,
           RCONA564 * 1.5,
           RCONA565 * 7.5,
           RCONA566 * 24,
           RCONA567 * 48,
           RCONA568 * 120,
           RCONA569 * 240,
           RCONA570 * 1.5,
           RCONA571 * 7.5,
           RCONA572 * 24,
           RCONA573 * 48,
           RCONA574 * 120,
           RCONA575 * 240, na.rm = T)/IEA,
         liabMatPeriod = sum(
           RCONA579 * 1.5, 
           RCONA580 * 7.5,
           RCONA581 * 24, 
           RCONA582 * 60, 
           RCONA584 * 1.5, 
           RCONA585 * 7.5, 
           RCONA586 * 24, 
           RCONA587 * 60, 
           RCONHK07 * 1.5, 
           RCONHK08 * 7.5, 
           RCONHK09 * 24, 
           RCONHK10 * 60, 
           RCONHK12 * 1.5, 
           RCONHK13 * 7.5, 
           RCONHK14 * 24, 
           RCONHK15 * 60,
           RCONF055 * 6,
           RCONF056 * 24,
           RCONF057 * 48,
           RCONF058 * 60,
           RCONF060 * 6,
           RCONF061 * 24,
           RCONF062 * 48,
           RCONF063 * 60,
           na.rm = T)/RCON2948,
         othAssets = RCON2170 - matAsset,
         othLiab = RCON2948 - matLiab,
         IRDerivOther = RCON8725,
         swapsTotal = RCON3450,
         IRDerivTrade = RCONA126,
         swapsFixed = RCONA589,
         swapsFloat = sum(RCON3450, -RCONA589, na.rm = T),
         assets = RCON2170,
         liab = RCON2948,
         equity = RCON3210,
         loans = RCON2122
  ) %>%
  select(RSSD9001, RSSD9999, IEA, matAsset, liab, equity, matLiab, savingDep, demandDep, timeDep, loans, niiRateAnn, nniRateAnn, roaAnn, niiLoansRateAnn, assetMatPeriod, liabMatPeriod, othAssets, othLiab, assets, IRDerivOther, swapsTotal, IRDerivTrade, swapsFixed, swapsFloat) %>%
  mutate(matGap = assetMatPeriod - liabMatPeriod,
         othAssetShare = othAssets/RCON2170,
         othLiabShare = othLiab/RCON2948) %>%
  ungroup()

write.csv(findf, "./Data/finalData/findf_RelSeries.csv")