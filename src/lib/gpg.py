#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2011 Martin Manns
# Distributed under the terms of the GNU General Public License

# --------------------------------------------------------------------
# pyspread is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyspread is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyspread.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------

"""

gpg
===

GPG handling functions

Provides
--------

 * is_pyme_present: Checks if pyme is installed
 * genkey: Generates gpg key
 * sign: Returns detached signature for file
 * verify: verifies stream against signature

"""

from config import config

try:
    from pyme import core, pygpgme
    import pyme.errors
except ImportError:
    pass
    

def is_pyme_present():
    """Returns True if pyme can be imported else false"""
    
    try:
        from pyme import core
        return True
    except ImportError:
        return False

def _passphrase_callback(hint='', desc='', prev_bad=''): 
    """Callback function needed by pyme"""
    
    return config["gpg_key_passphrase"]

def _get_file_data(filename):
    """Returns pyme.core.Data object of file."""
    
    # Required because of unicode bug in pyme
    
    infile = open(filename, "rb")
    infile_content = infile.read()
    infile.close()
    
    return core.Data(string=infile_content)


def genkey():
    """Creates a new standard GPG key"""
    
    # Initialize our context.
    core.check_version(None)

    c = core.Context()
    c.set_armor(1)
    #c.set_progress_cb(callbacks.progress_stdout, None)
    
    # Check if standard key is already present
    keyname = config["gpg_key_uid"]
    c.op_keylist_start(keyname, 0)
    key = c.op_keylist_next()
    if key is None:
        # Key not present --> Create new one
        print "Generating new GPG key", keyname, \
              ". This may take some time..."
        c.op_genkey(config["gpg_key_parameters"], None, None)
        print c.op_genkey_result().fpr



def sign(filename):
    """Returns detached signature for file"""
    
    plaintext = _get_file_data(filename)
    
    ciphertext = core.Data()
    
    ctx = core.Context()

    ctx.set_armor(1)
    ctx.set_passphrase_cb(_passphrase_callback)
    
    ctx.op_keylist_start(config["gpg_key_uid"], 0)
    sigkey = ctx.op_keylist_next()
    ##print sigkey.uids[0].uid
    
    ctx.signers_clear()
    ctx.signers_add(sigkey)
    
    ctx.op_sign(plaintext, ciphertext, pygpgme.GPGME_SIG_MODE_DETACH)
    
    ciphertext.seek(0, 0)
    signature = ciphertext.read()
    
    return signature

def verify(sigfilename, filefilename=None):
    """Verifies a signature, returns True if successful else False."""
    
    c = core.Context()

    # Create Data with signed text.
    __signature = _get_file_data(sigfilename)
    
    if filefilename:
        __file = _get_file_data(filefilename)
        __plain = None
    else:
        __file = None
        __plain = core.Data()

    # Verify.
    try:
        c.op_verify(__signature, __file, __plain)
    except pyme.errors.GPGMEError:
        return False
    
    result = c.op_verify_result()
    
    # List results for all signatures. Status equal 0 means "Ok".
    validation_sucess = False
    
    for sign in result.signatures:
        if (not sign.status) and sign.validity:
            validation_sucess = True
    
    return validation_sucess