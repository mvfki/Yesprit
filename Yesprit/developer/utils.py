'''For developer use only'''
import pickle
from Bio import SeqIO
import os

this_dir, this_filename = os.path.split(__file__)

def formatFasta(file_name, species, save = True):
    '''
    Load the text FASTA format file into a pickled data file, in the form of a 
    dictionary. 
    Arguments:
    ----------
    file_name - str
    species   - str, choose from {'P', 'J', 'O', 'C'}
    save      - bool, default True
    Returns:
    ----------
    fasta - dict
            With sequence names being the keys and the corresponding sequences 
            being the values.
    '''
    assert species in {'P', 'J', 'O', 'C'}
    destination = os.path.join(this_dir, 'data', species, 'seq.pkl')
    records = SeqIO.parse(file_name, 'fasta')
    fasta = {r.name: r.seq for r in records}
    if save:
        with open(destination, 'wb') as out:
            pickle.dump(fasta, out)
        out.close
    return fasta
