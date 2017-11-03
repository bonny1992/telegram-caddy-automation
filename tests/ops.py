import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import vhosts_ops as ops

def test_load():
    print('.Testing the load function...', end=' ')
    assert ops.load() == True
    print('OK')

def test_list_vhosts_db():
    print('Testing the list_vhosts_db function...', end=' ')
    assert len(ops.list_vhosts_db()) > -1
    print('OK')

def test_list_vhost_files():
    print('Testing the list_vhost_files function...', end=' ')
    assert(len(ops.list_vhost_files())) > -1
    print('OK')

def test_new_vhost():
    print('Testing the new_vhost function...', end=' ')
    assert ops.new_vhost('nosetest.bonny.pw', 'www.nosetest.bonny.pw', '127.0.0.1', '0') == True
    print('OK')

def test_delete_vhost():
    print('Testing the delete_vhost function...', end=' ')
    assert ops.delete_vhost('nosetest.bonny.pw') == True
    print('OK')
