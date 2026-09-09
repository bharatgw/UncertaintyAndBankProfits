"""Checks for the dated institution mapping in the merger notebook."""
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from contextlib import redirect_stdout


@unittest.skipUnless(importlib.util.find_spec('pandas'), 'Requires the data-processing Python environment')
class MergerPreparationTests(unittest.TestCase):
    def test_chains_splits_and_date_cutoff(self):
        import pandas as pd
        notebook = json.loads((Path(__file__).resolve().parents[2] / 'Data_2-MergerAdjust.ipynb').read_text())
        source = ''.join(next(c['source'] for c in notebook['cells'] if 'def getUltimateCompany' in ''.join(c['source'])))
        records = pd.DataFrame([
            (1, 2, 1, 1, 20010101),
            (2, 3, 1, 1, 20050101),
            (3, 4, 1, 1, 20240101),  # After the paper's mapping date.
            (10, 11, 1, 1, 20100101),
            (10, 12, 1, 1, 20100101),
            (20, 21, 5, 1, 20010101),  # A split does not dissolve the predecessor.
            (30, 31, 7, 1, 20010101),  # Sale of assets is excluded.
        ], columns=['#ID_RSSD_PREDECESSOR', 'ID_RSSD_SUCCESSOR', 'TRNSFM_CD', 'ACCT_METHOD', 'DT_TRANS'])
        scope = {'pd': pd}
        with patch.object(pd, 'read_csv', return_value=records), patch.object(pd.DataFrame, 'to_csv'), redirect_stdout(io.StringIO()):
            exec(source, scope)
        result = scope['transformations']
        self.assertEqual(list(zip(result.oldRSSD9001, result.ultimateCompany, result.nAcquirers)), [(1, 3, 1), (2, 3, 1), (10, 11, 2), (10, 12, 2)])
        self.assertEqual(set(scope['getUltimateCompany'](10, 10, {})), {11, 12})
        scope['successors'] = {1: [2], 2: [1]}
        with self.assertRaisesRegex(ValueError, 'Circular institution mapping'):
            scope['getUltimateCompany'](1, 1, {})


if __name__ == '__main__':
    unittest.main()
