library(seasonal)
library(lubridate)
library(tidyverse)

trimOutliers = function(v, thres){
  bounds = quantile(v, probs = c(thres, 1-thres), na.rm = T)
  
  v[v <= bounds[1]] = NA
  v[v >= bounds[2]] = NA
  
  return(v)
}

winsOutliers = function(v, thres){
  bounds = quantile(v, probs = c(thres, 1-thres), na.rm = T)
  
  v[v <= bounds[1]] = bounds[1]
  v[v >= bounds[2]] = bounds[2]
  
  return(v)
}

longestContiguousTS = function(series, dates, progressBar){
  progressBar$tick()$print()
  startDate = min(dates)
  startDate = c(year(startDate), quarter(startDate))
  endDate = max(dates)
  endDate = c(year(endDate), quarter(endDate))
  series = ts(series, start = startDate, end = endDate, frequency = 4)
  if (sum(is.na(series)) == length(series)){
    return(NA)
  }
  series = na.contiguous(series)
  series = bimets::TSEXTEND(series, BACKTO = startDate, UPTO = endDate, EXTMODE = "MISSING")
  return(series)
}

getSeasonallyAdjustedSeries = function(series, dates, progressBar){
  progressBar$tick()$print()
  startDate = min(dates)
  startDate = c(year(startDate), quarter(startDate))
  endDate = max(dates)
  endDate = c(year(endDate), quarter(endDate))
  series = ts(series, start = startDate, end = endDate, frequency = 4)
  seriesSA = try(seas(series, "x11" = ""), silent = TRUE)
  if (class(seriesSA) == "try-error"){
    seriesSA = try(seas(series, "x11" = "", outlier = NULL), silent = TRUE)
  }
  if (class(seriesSA) == "try-error"){
    return(NA)
  }
  return(series(seriesSA, "d11"))
}

englishFilter = function(df, outlierVar){
  
  print("Original")
  print(dim(df))
  # Asset growth is less than 20%
  df = df %>%
    filter(deltaLogASeasAdj <= 0.2)
  
  print("Dropping Company-Quarters with Asset Growth >= 20%")
  print(dim(df))
  
  # Average loan share for banks should be larger than 25%
  companyFilter = df %>%
    as_tibble() %>%
    group_by(RSSD9001) %>%
    summarize(meanloanShare = mean(loanShare, na.rm = T)) %>%
    filter(meanloanShare >= 0.25) %>%
    .$RSSD9001
  
  df = df %>%
    filter(RSSD9001 %in% companyFilter)
  
  print("Dropping companies with Mean Loan Share < 25%")
  print(dim(df))
  
  naCountBefore = df %>%
    select(outlierVar) %>%
    is.na() %>%
    sum()
  
  # Drop outliers
  df = df %>%
    mutate(across(outlierVar, .fns = function(x){winsOutliers(x, 0.01)}))
  
  naCountAfter = df %>%
    select(outlierVar) %>%
    is.na() %>%
    sum()
  
  print("Trimming outliers at the 1% level in outlierVars")
  print(paste("This introduces", naCountAfter - naCountBefore, "NAs"))
  
  print(dim(df))
  
  # Eliminate banks with less than 24 quarters of observations
  
  companyFilter = df %>%
    dplyr::count(RSSD9001) %>%
    filter(n >= 24) %>%
    .$RSSD9001
  
  df = df %>%
    filter(RSSD9001 %in% companyFilter) %>%
    as_tsibble(key = RSSD9001, index = RSSD9999)
  
  print("Dropping companies with less than 24 consecutive quarters")
  print(dim(df))
  
  return(df)
  
}