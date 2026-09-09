"""Validate seasonal failure reporting without requiring a local X13 binary."""
import ast
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
import unittest
from unittest.mock import Mock
import warnings


@unittest.skipUnless(importlib.util.find_spec('pandas'), 'Requires the data-processing Python environment')
class SeasonalReportingTests(unittest.TestCase):
    def test_success_failure_and_interrupt(self):
        import numpy as np
        import pandas as pd
        source = (Path(__file__).resolve().parents[2] / 'Data_5-SeasonalAdjust.py').read_text()
        function = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef))
        backend = Mock(return_value=Mock(seasadj=Mock(values=np.array([1., 2., 3.]))))
        scope = {'pd': pd, 'nan': np.nan, 'warnings': warnings, 'TemporaryDirectory': TemporaryDirectory,
                 'x13_arima_analysis': backend, 'seasonal_failures': []}
        exec(compile(ast.Module(body=[function], type_ignores=[]), '<seasonal-function>', 'exec'), scope)
        series = pd.Series([1., 2., 3.], index=pd.period_range('2000Q1', periods=3, freq='Q'), name='NIM')
        adjust = scope['getSeasonallyAdjustedSeries']
        np.testing.assert_array_equal(adjust(series, Mock(), bank_id=1), [1., 2., 3.])
        self.assertFalse(Path(backend.call_args.kwargs['tempdir']).exists())
        self.assertEqual(scope['seasonal_failures'], [])
        backend.side_effect = ValueError('insufficient observations')
        self.assertTrue(np.isnan(adjust(series, Mock(), bank_id=2)))
        failure = scope['seasonal_failures'][0]
        self.assertEqual((failure['RSSD9001'], failure['series'], failure['error_type']), (2, 'NIM', 'ValueError'))
        backend.side_effect = KeyboardInterrupt
        with self.assertRaises(KeyboardInterrupt):
            adjust(series, Mock(), bank_id=3)


    def test_concurrent_banks_preserve_serial_values_and_order(self):
        import numpy as np
        import pandas as pd
        source = (Path(__file__).resolve().parents[2] / 'Data_5-SeasonalAdjust.py').read_text()
        functions = [n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef)]
        scope = {'pd': pd, 'nan': np.nan, 'warnings': warnings, 'TemporaryDirectory': TemporaryDirectory,
                 'x13_arima_analysis': lambda series, **kwargs: SimpleNamespace(seasadj=series * 2),
                 'seasonal_failures': [], 'pb_Season': Mock(), 'relCols': ['profit']}
        exec(compile(ast.Module(body=functions, type_ignores=[]), '<seasonal-functions>', 'exec'), scope)
        dates = pd.date_range('2000-01-01', periods=4, freq='QS')
        data = pd.concat([pd.DataFrame({'RSSD9001': bank, 'profit': np.arange(4.) + bank}, index=dates)
                          for bank in [3, 1, 2]]).rename_axis('RSSD9999')
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            serial = data.groupby('RSSD9001').apply(lambda bank: bank.assign(
                profitSeasAdj=scope['getSeasonallyAdjustedSeries'](bank.profit, scope['pb_Season'], bank.name)))
        groups = list(data.groupby('RSSD9001', sort=True))
        with ThreadPoolExecutor(max_workers=3) as executor:
            frames = list(executor.map(scope['adjustBank'], groups))
        parallel = pd.concat(frames, keys=[bank for bank, _ in groups], names=['RSSD9001'])
        pd.testing.assert_frame_equal(serial, parallel, check_exact=True)
        self.assertEqual(scope['seasonal_failures'], [])


if __name__ == '__main__':
    unittest.main()
