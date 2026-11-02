"""SQLite solver repository independent of existing MCT training database."""
import json,sqlite3
from solver_import import validate
class SolverRepository:
    def __init__(self,path='mct_solvers.sqlite3'):
        self.conn=sqlite3.connect(path,check_same_thread=False)
        self.conn.execute('CREATE TABLE IF NOT EXISTS solutions (id TEXT PRIMARY KEY, data TEXT NOT NULL)')
        self.conn.commit()
    def save(self,solution):
        s=validate(solution)
        self.conn.execute('INSERT OR REPLACE INTO solutions VALUES (?,?)',(s['id'],json.dumps(s)))
        self.conn.commit()
    def load(self,id):
        row=self.conn.execute('SELECT data FROM solutions WHERE id=?',(id,)).fetchone()
        return json.loads(row[0]) if row else None
    def list(self):
        return [dict(id=r[0],solver=json.loads(r[1])['solver']['name'],source=json.loads(r[1])['source']['verification']) for r in self.conn.execute('SELECT id,data FROM solutions ORDER BY id')]
    def delete(self,id):
        self.conn.execute('DELETE FROM solutions WHERE id=?',(id,));self.conn.commit()
    def backup(self):
        return json.dumps({'schema':'mct.solver.backup.v1','solutions':[json.loads(r[0]) for r in self.conn.execute('SELECT data FROM solutions')]},indent=2).encode()
    def restore(self,blob):
        obj=json.loads(blob)
        if obj.get('schema')!='mct.solver.backup.v1' or not isinstance(obj.get('solutions'),list): raise ValueError('Unsupported backup')
        validated=[validate(x) for x in obj['solutions']]
        with self.conn:
            for x in validated:self.conn.execute('INSERT OR REPLACE INTO solutions VALUES (?,?)',(x['id'],json.dumps(x)))
        return len(validated)
