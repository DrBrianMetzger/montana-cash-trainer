"""Shared SQLite store. Cloud local disk is ephemeral; use full JSON backup."""
import json, sqlite3, uuid
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 1
SOURCES = ('montana_practice','pluribus_prediction','gto_exact','live_review')
TABLES = ('sessions','practice_hands','decisions','personas','pluribus_predictions','gto_references','solver_screenshots','leaks','progress')

def now(): return datetime.now(timezone.utc).isoformat()
def uid(): return uuid.uuid4().hex

class TrainingDB:
    def __init__(self, path=None):
        self.path=str(path or Path(__file__).with_name('trainer.sqlite3'))
        self.initialize()
    def connect(self):
        db=sqlite3.connect(self.path,timeout=10)
        db.row_factory=sqlite3.Row
        db.execute('PRAGMA busy_timeout=10000')
        return db
    def initialize(self):
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, created_utc TEXT, source TEXT, metadata TEXT)')
            db.execute('CREATE TABLE IF NOT EXISTS practice_hands (id TEXT PRIMARY KEY, session_id TEXT, created_utc TEXT, state TEXT, outcome TEXT)')
            db.execute('CREATE TABLE IF NOT EXISTS decisions (id TEXT PRIMARY KEY, session_id TEXT, hand_id TEXT, created_utc TEXT, source TEXT, street TEXT, action TEXT, context TEXT, feedback TEXT)')
            db.execute('CREATE TABLE IF NOT EXISTS personas (id TEXT PRIMARY KEY, name TEXT, profile TEXT, updated_utc TEXT)')
            db.execute('CREATE TABLE IF NOT EXISTS pluribus_predictions (id TEXT PRIMARY KEY, decision_id TEXT, hand_key TEXT UNIQUE, guess TEXT, actual TEXT, street TEXT, created_utc TEXT)')
            db.execute('CREATE TABLE IF NOT EXISTS gto_references (id TEXT PRIMARY KEY, data TEXT, updated_utc TEXT)')
            db.execute('CREATE TABLE IF NOT EXISTS solver_screenshots (id TEXT PRIMARY KEY, reference_id TEXT, mime TEXT, image_b64 TEXT)')
            db.execute('CREATE TABLE IF NOT EXISTS leaks (id TEXT PRIMARY KEY, decision_id TEXT, category TEXT, notes TEXT, created_utc TEXT)')
            db.execute('CREATE TABLE IF NOT EXISTS progress (id TEXT PRIMARY KEY, metric TEXT, value REAL, source TEXT, updated_utc TEXT)')
    def insert(self,table,values,replace=False):
        if table not in TABLES: raise ValueError('Unknown table')
        fields=list(values)
        if not set(fields).issubset({r[1] for r in self.columns(table)}): raise ValueError('Unknown column')
        sql=('INSERT OR REPLACE' if replace else 'INSERT OR IGNORE')+f' INTO {table} ('+','.join(fields)+') VALUES ('+','.join('?' for _ in fields)+')'
        with self.connect() as db: db.execute(sql,[values[k] for k in fields])
    def columns(self,table):
        with self.connect() as db: return db.execute(f'PRAGMA table_info({table})').fetchall()
    def rows(self,table):
        if table not in TABLES: raise ValueError('Unknown table')
        with self.connect() as db: return [dict(x) for x in db.execute(f'SELECT * FROM {table}')]
    def start_session(self,source,metadata=None):
        if source not in SOURCES: raise ValueError('Unknown source')
        key=uid(); self.insert('sessions',dict(id=key,created_utc=now(),source=source,metadata=json.dumps(metadata or {}))); return key
    def decision(self,session_id,source,street,action,context=None,feedback='',hand_id=None):
        if source not in SOURCES: raise ValueError('Unknown source')
        key=uid(); self.insert('decisions',dict(id=key,session_id=session_id,hand_id=hand_id,created_utc=now(),source=source,street=street,action=action,context=json.dumps(context or {}),feedback=feedback)); return key
    def save_prediction(self,session_id,hand_key,guess,actual,street,context=None):
        with self.connect() as db:
            existing=db.execute('SELECT * FROM pluribus_predictions WHERE hand_key=?',(hand_key,)).fetchone()
        if existing: return False
        decision_id=self.decision(session_id,'pluribus_prediction',street,guess,dict(context or {},recorded_action=actual))
        self.insert('pluribus_predictions',dict(id=uid(),decision_id=decision_id,hand_key=hand_key,guess=guess,actual=actual,street=street,created_utc=now()))
        return True
    def save_reference(self,item):
        data=dict(item); image=data.pop('image_b64',None)
        self.insert('gto_references',dict(id=str(data['id']),data=json.dumps(data),updated_utc=now()),replace=True)
        if image:
            self.insert('solver_screenshots',dict(id=str(data['id']),reference_id=str(data['id']),mime=data.get('image_mime','image/png'),image_b64=image),replace=True)
    def references(self):
        images={x['reference_id']:x for x in self.rows('solver_screenshots')}
        out=[]
        for r in self.rows('gto_references'):
            item=json.loads(r['data'])
            if r['id'] in images: item['image_b64']=images[r['id']]['image_b64']
            out.append(item)
        return out
    def backup(self): return json.dumps({'format':'montana-trainer-backup','version':SCHEMA_VERSION,'tables':{t:self.rows(t) for t in TABLES}},indent=2)
    def restore(self,blob):
        data=json.loads(blob) if isinstance(blob,(str,bytes)) else blob
        if data.get('format')!='montana-trainer-backup' or data.get('version')!=SCHEMA_VERSION: raise ValueError('Unsupported backup format/version')
        tables=data.get('tables')
        if not isinstance(tables,dict) or set(tables)!=set(TABLES): raise ValueError('Backup missing tables')
        # Validate all data before making any writes.
        for t,rows in tables.items():
            cols={r[1] for r in self.columns(t)}
            if not isinstance(rows,list) or any(not isinstance(row,dict) or 'id' not in row or not set(row).issubset(cols) for row in rows): raise ValueError(f'Invalid {t} records')
        count=0
        for t,rows in tables.items():
            for row in rows: self.insert(t,row); count+=1
        return count
