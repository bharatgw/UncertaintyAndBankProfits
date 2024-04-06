import pandas as pd
from statsmodels.tsa.x13 import x13_arima_analysis
from tqdm import tqdm
import warnings
from numpy import nan

df = pd.read_csv("./Data/finalData/findf_RelSeriesContiguous.csv", low_memory=False, index_col = 0)
qs = df['RSSD9999'].str.replace(r' ', r'-')
df["RSSD9999"] = pd.PeriodIndex(qs, freq='Q').to_timestamp()

def getSeasonallyAdjustedSeries(series, progressBar):
    progressBar.update(1)
    series.index = pd.PeriodIndex(series.index, freq='Q')
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            seriesSA = x13_arima_analysis(series,  x12path = "./x13as/").seasadj.values
    except:
        seriesSA = nan
    return seriesSA

relCols = ['intExpenseRateAnn', 'intIncomeRateAnn', 'niiRateAnn', 'nniRateAnn', 'roaAnn', 'deltaLogA', "intIncLoans", "intIncFed", "intIncOthSec", "IntIncTrade", "intIncDepInst", "intExpDep", "intExpTrade", "intExpNotes", "intIncSec", "LoanProvision", "othIntInc", "othIntExp"]
dropCols = ['intExpenseRateAnn', 'intIncomeRateAnn', 'niiRateAnn', 'nniRateAnn', 'roaAnn', 'deltaLogA']

pb_Season = tqdm(total=len(df['RSSD9001'].unique())*len(relCols))
df = df.set_index('RSSD9999').groupby(by='RSSD9001').apply(lambda x: x.assign(**{f'{col}SeasAdj': getSeasonallyAdjustedSeries(x[col], pb_Season) for col in relCols})).dropna(subset=[f'{col}SeasAdj' for col in dropCols])

print(df.shape)
df.to_csv("./Data/finalData/findf_RelSeriesContiguousSA.csv")