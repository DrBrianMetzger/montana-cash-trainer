"""Eight/nine-seat Montana practice: card dealing, positional turns and conservative cap-safe wagering.

Simulation model, not a casino-certified betting implementation. All amounts in cents.
"""
from dataclasses import dataclass, field
import random
from collections import Counter
from itertools import combinations

RANKS='23456789TJQKA'; SUITS='cdhs'; CAP=80000

def cards(): return [r+s for r in RANKS for s in SUITS]
def fmt(c): return f'${c/100:,.2f}'
def strength(hand):
    a,b=(RANKS.index(c[0]) for c in hand)
    high=max(a,b); low=min(a,b)
    if a==b: return 60+high*3
    return high*3+low*.6+(7 if hand[0][1]==hand[1][1] else 0)+(4 if high-low==1 else 0)

def rank_five(hand):
    """Comparable five-card high-hand rank (no wild cards)."""
    values=sorted((RANKS.index(c[0])+2 for c in hand),reverse=True)
    count=Counter(values)
    flush=len({c[1] for c in hand})==1
    uniq=set(values)
    if 14 in uniq:uniq.add(1)
    straight=max((h for h in range(5,15) if set(range(h-4,h+1))<=uniq),default=0)
    if flush and straight:return (8,straight)
    groups=sorted(((n,v) for v,n in count.items()),reverse=True)
    if groups[0][0]==4:return (7,groups[0][1],groups[1][1])
    if groups[0][0]==3 and groups[1][0]==2:return (6,groups[0][1],groups[1][1])
    if flush:return (5,*values)
    if straight:return (4,straight)
    if groups[0][0]==3:return (3,groups[0][1],*sorted((v for v in values if v!=groups[0][1]),reverse=True))
    pairs=sorted((v for v,n in count.items() if n==2),reverse=True)
    if len(pairs)==2:return (2,*pairs,max(v for v in values if v not in pairs))
    if len(pairs)==1:return (1,pairs[0],*sorted((v for v in values if v!=pairs[0]),reverse=True))
    return (0,*values)

def rank_seven(hand):
    return max(rank_five(c) for c in combinations(hand,5))

@dataclass
class Seat:
    name:str
    stack:int
    house:bool=False
    cards:list=field(default_factory=list)
    street:int=0
    total:int=0
    folded:bool=False
    all_in:bool=False

class Table:
    def __init__(self,n=8,shill=False,seed=None):
        if n not in range(4,10): raise ValueError('Table size must be 4–9')
        self.rng=random.Random(seed);self.n=n;self.shill=shill
        names=['You','SantiNobu','PedaltotheMetalLisa','MoleculeMike','HelenaHomie','Montana Regular A','Montana Regular B','Montana Regular C','Montana Regular D']
        if shill: names[n-1]='House Shill'
        self.seats=[Seat(name,20000 if name=='House Shill' else 40000, name=='House Shill') for name in names[:n]]
        self.button=n-1;self.hand_no=0;self.house_buyins=20000 if shill else 0;self.house_rebuys=0;self.house_net=0;self.rake_total=0
        self.start()
    def start(self):
        self.hand_no+=1;self.button=(self.button+1)%self.n
        self.street='Preflop';self.board=[];self.pot=0;self.history=[];self.ended=False;self.outcome='';self.highest=0;self.min_raise=200
        deck=cards();self.rng.shuffle(deck);self.deck=deck
        for s in self.seats:
            if s.stack<=0:
                if s.house: s.stack=20000;self.house_buyins+=20000;self.house_rebuys+=1
                else: s.stack=40000
            s.cards=[deck.pop(),deck.pop()];s.street=0;s.total=0;s.folded=False;s.all_in=False
        self.sb=(self.button+1)%self.n;self.bb=(self.button+2)%self.n
        self._post(self.sb,100);self._post(self.bb,200)
        self.highest=200
        self.pending=[(self.bb+1+i)%self.n for i in range(self.n)]
        self.to_act=self.pending[0]
        self.history.append(f'Hand {self.hand_no}: blinds {self.seats[self.sb].name} $1, {self.seats[self.bb].name} $2')
        self._auto_until_hero()
    def _post(self,i,cents):
        s=self.seats[i];v=min(cents,s.stack);s.stack-=v;s.street+=v;s.total+=v;self.pot+=v;s.all_in=s.stack==0
    def active(self): return [i for i,s in enumerate(self.seats) if not s.folded]
    def can_act(self,i): return not self.seats[i].folded and not self.seats[i].all_in
    def to_call(self,i):return max(0,self.highest-self.seats[i].street)
    def position(self,i):
        if i==self.button:return 'BTN'
        if i==self.sb:return 'SB'
        if i==self.bb:return 'BB'
        order=[(self.bb+1+j)%self.n for j in range(self.n-3)]
        labels={4:['UTG'],5:['UTG','CO'],6:['UTG','HJ','CO'],7:['UTG','LJ','HJ','CO'],8:['UTG','UTG+1','LJ','HJ','CO'],9:['UTG','UTG+1','UTG+2','LJ','HJ','CO']}[self.n]
        return labels[order.index(i)]
    def legal(self,i):
        if self.ended or self.to_act!=i or not self.can_act(i):return []
        due=self.to_call(i)
        out=['Fold','Call'] if due else ['Check']
        if self.seats[i].stack>due and self.pot<CAP:out+=['Raise' if due else 'Bet']
        return out
    def _cap_extra(self,i):
        # Reserve a matching contribution from every currently active opponent.
        # This is deliberately conservative for multiway pots, not a full side-pot solver.
        eligible=sum(self.can_act(j) for j in self.active() if j!=i)
        return max(0,(CAP-self.pot)//max(1,eligible+1))
    def act(self,i,action,amount=0,automatic=False):
        if action not in self.legal(i):raise ValueError('Illegal action')
        s=self.seats[i];due=self.to_call(i);was_highest=self.highest
        if action=='Fold':s.folded=True;self.history.append(f'{s.name} folds')
        elif action=='Check':self.history.append(f'{s.name} checks')
        elif action=='Call':
            pay=min(due,s.stack,CAP-self.pot);self._post(i,pay)
            self.history.append(f'{s.name} calls {fmt(pay)}')
        else:
            # Amount is announced total for this street. Actual wager is capped.
            announced=int(round(float(amount)*100))
            if announced<=self.highest:raise ValueError('Bet/raise must exceed current bet')
            if announced<self.highest+self.min_raise and announced<s.street+s.stack:raise ValueError('Below minimum full raise')
            max_new=min(s.stack,self._cap_extra(i))
            added=min(announced-s.street,max_new)
            if added<=due:raise ValueError('No room for a legal raise under the pot cap')
            self._post(i,added)
            self.highest=s.street
            if self.highest-was_highest>=self.min_raise:self.min_raise=self.highest-was_highest
            self.history.append(f'{s.name} announces {fmt(announced)}; effective total {fmt(s.street)}')
            # Fresh action for every other live, non-all-in player after a raise.
            self.pending=[j for j in [(i+1+k)%self.n for k in range(self.n-1)] if self.can_act(j)]
        if i in self.pending:self.pending.remove(i)
        if len(self.active())==1:
            winner=self.active()[0];self.ended=True;self._award_uncontested(winner);return
        if self.pot>=CAP:
            self.history.append('Gross $800 cap reached; betting ends');self._runout();return
        if not self.pending:self._next_street()
        else:self.to_act=self.pending[0]
        if not automatic:self._auto_until_hero()
    def _next_street(self):
        if self.street=='River':self._showdown();return
        self.street={'Preflop':'Flop','Flop':'Turn','Turn':'River'}[self.street]
        self.board.extend(self.deck.pop() for _ in range(3 if self.street=='Flop' else 1))
        for s in self.seats:s.street=0
        self.highest=0;self.min_raise=200
        self.pending=[j for j in [(self.button+1+k)%self.n for k in range(self.n)] if self.can_act(j)]
        self.history.append(f'{self.street}: {" ".join(self.board)}')
        if not self.pending:self._runout()
        else:self.to_act=self.pending[0]
    def _runout(self):
        while len(self.board)<5:self.board.append(self.deck.pop())
        self.street='Showdown';self._showdown()
    def _rake(self):
        # 10% of gross pot, capped at $6. Gross pot already includes rake.
        return min(600,(self.pot+9)//10)
    def _award_uncontested(self,winner):
        rake=self._rake();self.rake_total+=rake
        self.seats[winner].stack+=self.pot-rake
        self.outcome=f'{self.seats[winner].name} wins {fmt(self.pot-rake)} after {fmt(rake)} rake'
        self.history.append(self.outcome)
    def _showdown(self):
        self.ended=True
        contenders=self.active()
        if len(contenders)==1:self._award_uncontested(contenders[0]);return
        if len(self.board)<5:
            while len(self.board)<5:self.board.append(self.deck.pop())
        rankings={i:rank_seven(self.seats[i].cards+self.board) for i in contenders}
        # Side pots based on total invested by each player, including folded contributions.
        levels=sorted({s.total for s in self.seats if s.total>0})
        previous=0;payout=[0]*self.n
        rake_remaining=self._rake();rake=rake_remaining
        for level in levels:
            participants=[i for i,s in enumerate(self.seats) if s.total>=level]
            side=(level-previous)*len(participants);previous=level
            if not side:continue
            taken=min(side,rake_remaining);side-=taken;rake_remaining-=taken
            eligible=[i for i in participants if i in rankings]
            if not eligible:
                # Uncalled excess: return to the sole contributor, rather than awarding dead chips.
                if len(participants)==1:payout[participants[0]]+=side
                continue
            best=max(rankings[i] for i in eligible)
            winners=[i for i in eligible if rankings[i]==best]
            share,extra=divmod(side,len(winners))
            for i in winners:payout[i]+=share
            for i in sorted(winners)[:extra]:payout[i]+=1
        self.rake_total+=rake
        for i,v in enumerate(payout):self.seats[i].stack+=v
        winners=[f'{self.seats[i].name} {fmt(v)}' for i,v in enumerate(payout) if v]
        self.outcome='Showdown: '+', '.join(winners)+f' (rake {fmt(rake)})'
        self.history.append(self.outcome)
    def _auto_until_hero(self):
        for _ in range(100):
            if self.ended or self.to_act==0:return
            i=self.to_act;s=self.seats[i];due=self.to_call(i);score=strength(s.cards)
            # Explicitly heuristic, not solver-derived or calibrated from observed player data.
            threshold=78 if s.house else (64 if s.name=='MoleculeMike' else 52 if s.name=='HelenaHomie' else 43)
            if self.street=='Preflop':
                if due and score<threshold:choice='Fold'
                elif due:choice='Call'
                else:choice='Check'
                if s.house and score>=90 and self._cap_extra(i)>due+200 and 'Raise' in self.legal(i):
                    self.act(i,'Raise',max((self.highest+200)/100,20),True);continue
            else:
                if due and s.house and score<95:choice='Fold'
                elif due and score<35:choice='Fold'
                elif due:choice='Call'
                else:choice='Check'
            if choice not in self.legal(i):choice=self.legal(i)[0]
            self.act(i,choice,automatic=True)
        raise RuntimeError('Automatic turn loop did not terminate')
