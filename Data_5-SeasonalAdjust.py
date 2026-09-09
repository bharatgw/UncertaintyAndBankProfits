import pandas as pd
from statsmodels.tsa.x13 import x13_arima_analysis, _find_x12
from tqdm import tqdm
import warnings
from numpy import nan
from pathlib import Path
from tempfile import TemporaryDirectory
from concurrent.futures import ThreadPoolExecutor
import os

if not _find_x12("./x13as/"):
    raise FileNotFoundError("A working X13 executable is required under x13as/.")

seasonal_failures = []

df = pd.read_csv("./Data/finalData/findf_RelSeriesContiguous.csv", low_memory=False, index_col = 0)
qs = df['RSSD9999'].str.replace(r' ', r'-')
df["RSSD9999"] = pd.PeriodIndex(qs, freq='Q').to_timestamp()

def getSeasonallyAdjustedSeries(series, progressBar, bank_id=None):
    progressBar.update(1)
    series.index = pd.PeriodIndex(series.index, freq='Q')
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with TemporaryDirectory(prefix="thesis-x13-") as directory:
                seriesSA = x13_arima_analysis(series, x12path="./x13as/", tempdir=directory).seasadj.values
    except Exception as error:
        seasonal_failures.append({
            "RSSD9001": bank_id, "series": series.name, "observations": len(series),
            "error_type": type(error).__name__, "error": str(error).strip(),
        })
        seriesSA = nan
    return seriesSA

relCols = ['intExpenseRateAnn', 'intIncomeRateAnn', 'niiRateAnn', 'nniRateAnn', 'roaAnn', 'deltaLogA', "intIncLoans", "intIncFed", "intIncOthSec", "IntIncTrade", "intIncDepInst", "intExpDep", "intExpTrade", "intExpNotes", "intIncSec", "LoanProvision", "othIntInc", "othIntExp"]
dropCols = ['intExpenseRateAnn', 'intIncomeRateAnn', 'niiRateAnn', 'nniRateAnn', 'roaAnn', 'deltaLogA']

pb_Season = tqdm(total=len(df['RSSD9001'].unique())*len(relCols))
def adjustBank(bank_group):
    bank_id, bank = bank_group
    return bank.assign(**{
        f"{col}SeasAdj": getSeasonallyAdjustedSeries(bank[col], pb_Season, bank_id=bank_id)
        for col in relCols
    })


workers = int(os.environ.get("THESIS_X13_WORKERS", "1"))
if workers < 1:
    raise ValueError("THESIS_X13_WORKERS must be positive.")
bank_groups = list(df.set_index("RSSD9999").groupby("RSSD9001", sort=True))
with ThreadPoolExecutor(max_workers=workers) as executor:
    adjusted_banks = list(executor.map(adjustBank, bank_groups))
df = pd.concat(adjusted_banks, keys=[bank_id for bank_id, _ in bank_groups], names=["RSSD9001"])
df = df.dropna(subset=[f"{col}SeasAdj" for col in dropCols])

pb_Season.close()
Path("outputs/paper").mkdir(parents=True, exist_ok=True)
pd.DataFrame(seasonal_failures, columns=["RSSD9001", "series", "observations", "error_type", "error"]).sort_values(["RSSD9001", "series"]).to_csv("outputs/paper/seasonal_adjustment_failures.csv", index=False)
print(f"Seasonal adjustment failures: {len(seasonal_failures):,}")
if df.empty:
    raise RuntimeError("No bank observations survived seasonal adjustment; inspect the failure report.")
print(df.shape)
df.to_csv("./Data/finalData/findf_RelSeriesContiguousSA.csv")