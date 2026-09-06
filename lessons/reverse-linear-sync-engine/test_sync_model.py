import unittest
from sync_model import TeachingClient

class TeachingModelTests(unittest.TestCase):
    def test_remote_base_does_not_hide_pending_edit(self):
        c=TeachingClient('original',100);c.edit('mine','Bob');c.receive('Alice',101)
        self.assertEqual((c.base,c.visible),('Alice','Bob'))
    def test_ack_waits_until_required_position(self):
        c=TeachingClient('original',100);c.edit('mine','Bob');c.acknowledge('mine',102)
        c.receive('Alice',101);self.assertEqual(len(c.pending),1)
        c.receive('Bob',102);self.assertEqual((c.visible,len(c.pending)),('Bob',0))
    def test_delta_before_ack(self):
        c=TeachingClient('original',100);c.edit('mine','Bob');c.receive('Bob',102)
        c.acknowledge('mine',102);self.assertEqual(len(c.pending),0)
    def test_rejection_exposes_updated_base(self):
        c=TeachingClient('original',100);c.edit('mine','Bob');c.receive('Alice',101)
        c.reject('mine');self.assertEqual(c.visible,'Alice')
    def test_newer_local_operation_survives_older_completion(self):
        c=TeachingClient('original',100);c.edit('first','Bob');c.edit('second','Carol')
        c.acknowledge('first',101);c.receive('Bob',101)
        self.assertEqual(c.visible,'Carol');self.assertEqual(len(c.pending),1)
    def test_stale_delta_does_not_rewind(self):
        c=TeachingClient('Bob',102);c.receive('Alice',101)
        self.assertEqual((c.base,c.sync_id),('Bob',102))

if __name__=='__main__':unittest.main()
