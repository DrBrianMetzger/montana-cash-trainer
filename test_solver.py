import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from solver_models import hand_classes,combos
from solver_import import validate
from solver_repository import SolverRepository
from range_matrix import summarize
from combo_explorer import combo_rows
FIX=Path(__file__).with_name('synthetic_fixture.json')
class SolverTests(unittest.TestCase):
 def setUp(self):self.sol=json.loads(FIX.read_text())
 def test_matrix(self):self.assertEqual(len(set(hand_classes())),169)
 def test_combos(self):
  self.assertEqual(len(combos('AA')),6)
  self.assertEqual(len(combos('AKs')),4)
  self.assertEqual(len(combos('AKo')),12)
  self.assertEqual(len(combos('AKs',['As'])),3)
 def test_validate(self):self.assertEqual(validate(self.sol)['id'],'synthetic_demo')
 def test_bad_freq(self):
  self.sol['nodes'][0]['combos']['As Ks']['frequencies']['Check']=40
  with self.assertRaises(ValueError):validate(self.sol)
 def test_blocker(self):
  self.sol['nodes'][0]['board']=['As','7d','2c']
  with self.assertRaises(ValueError):validate(self.sol)
 def test_weighted(self):
  x=summarize(self.sol['nodes'][0])['AKs']
  self.assertAlmostEqual(x['actions']['Check'],(0.5*75+1*25)/1.5)
 def test_combo(self):self.assertEqual(len(combo_rows(self.sol['nodes'][0],'AKs')),2)
 def test_backup(self):
  with tempfile.TemporaryDirectory() as t:
   a=SolverRepository(str(Path(t)/'a.db'));a.save(self.sol)
   b=SolverRepository(str(Path(t)/'b.db'));self.assertEqual(b.restore(a.backup()),1)
   self.assertEqual(b.load('synthetic_demo')['id'],'synthetic_demo')
if __name__=='__main__':unittest.main()
