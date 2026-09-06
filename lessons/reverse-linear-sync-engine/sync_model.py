"""Original teaching model, NOT a reconstruction of Linear's implementation.

Only one scalar field is modeled. No networking, permissions or persistence.
Keep a confirmed base and overlay outstanding local operations in order.
"""
from dataclasses import dataclass

@dataclass
class Operation:
    identifier: str
    value: str
    acknowledged_at: int | None = None

class TeachingClient:
    def __init__(self,value,sync_id=0):
        self.base=value;self.sync_id=sync_id;self.pending=[]
    @property
    def visible(self):return self.pending[-1].value if self.pending else self.base
    def edit(self,identifier,value):
        if any(x.identifier==identifier for x in self.pending):raise ValueError('duplicate operation')
        self.pending.append(Operation(identifier,value))
    def acknowledge(self,identifier,required_sync_id):
        operation=next(x for x in self.pending if x.identifier==identifier)
        operation.acknowledged_at=required_sync_id
        self._retire()
    def receive(self,value,sync_id):
        if sync_id<=self.sync_id:return
        self.base=value;self.sync_id=sync_id;self._retire()
    def reject(self,identifier):
        self.pending=[x for x in self.pending if x.identifier!=identifier]
    def _retire(self):
        self.pending=[x for x in self.pending if x.acknowledged_at is None or x.acknowledged_at>self.sync_id]

if __name__=='__main__':
    c=TeachingClient('original',100);c.edit('mine','Bob')
    print('edit:',c.base,c.visible)
    c.receive('Alice',101);print('remote:',c.base,c.visible)
    c.acknowledge('mine',102);print('ack:',c.base,c.visible,len(c.pending))
    c.receive('Bob',102);print('synced:',c.base,c.visible,len(c.pending))
