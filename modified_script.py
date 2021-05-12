import os
import sys
import re
import subprocess
import urllib.parse
import urllib.request
import time
import datetime
url = 'https://www.uniprot.org/uploadlists/'

this_dir, this_filename = os.path.split(__file__)
IDPath = os.path.join(this_dir,'resources','IDs.txt')
PFastPath = os.path.join(this_dir,'resources','4species.fasta')
SeqPath = os.path.join(this_dir,'resources','sequence.fasta')
BlaPath = os.path.join(this_dir,'resources','blastp_out.txt')


f1 = open(PFastPath,'r').readlines()
fadict={}
for i in f1:
    if i.startswith('>'):
        k = i.strip("\n").split('|')
        id = k[1]
        fa=''
    else:
        fa = fa + i.strip("\n")
        fadict[id]=fa

def search(keyword,species,dica = fadict):
    proteinlist = []
    e_valuelist = []
    score_bits = []
    per_identity = []
    descri_word = []
    f = open(IDPath,'r')
    for lines in f:
        lines = lines.strip('\n').split('\t')
        if keyword == lines[0]:
            keywords = lines[1]
    f3 = open(SeqPath,'w')
    for key in dica:
        if keywords == key:
            id = keywords
            fa = dica[keywords]
            f3.write('>'+id+'\n'+fa+'\n')
    f3.close()
    blastPPath = os.path.join(this_dir, 'lib', 'blastp.exe')
    if species == "J":
        dbPath = os.path.join(this_dir, 'data', species, 'japonicus.fasta')
    elif species == "P":
        dbPath = os.path.join(this_dir, 'data', species, 'Pombe.fasta')
    elif species == "O":
        dbPath = os.path.join(this_dir, 'data', species, 'octosporus.fasta')
    elif species == "C":
        dbPath = os.path.join(this_dir, 'data', species, 'cryophilus.fasta')
    else:
        print("wrong species parameter!")
    cmd = '{} -task blastp -query {} -db {} -out {}'.format(blastPPath,SeqPath, dbPath, BlaPath)
    os.popen(cmd)
    time.sleep(3)
    f.close()
    with open(BlaPath,'r') as f:
        lines = f.readlines()
        for i in lines:
            if i.startswith('tr|'):
                element = i.split('|')[1]
                proteinlist.append(element)
                if species == 'J':
                    word = re.split('_SCHJY|OS=', i)[1]
                elif species == 'O':
                    word = re.split('_SCHOY|OS=', i)[1]
                elif species == 'C':
                    word = re.split('_SCHCR|OS=', i)[1]
                word = word.strip(' ')
                descri_word.append(word)
                extract_evalue = i.strip(' \n').split(' ')[-1]
                e_valuelist.append(extract_evalue)
                score = i.strip(' \n').split(' ')[-5]
                score_bits.append(score)
            elif 'Identities' in i:
                iden = re.split(r'[()]',i)[1]
                per_identity.append(iden)       
    f.close()
    corresponding_geneID = []
    if len(proteinlist) >= 5:#len(proteinlist)
        for i in range(5):
            params = {
            'from': 'ACC+ID',
            'to': 'ENSEMBLGENOME_ID',#P_ENTREZGENEID,P_REFSEQ_AC ,REFSEQ_NT_ID
            'format': 'tab',
            'query': proteinlist[i]
            }
            data = urllib.parse.urlencode(params)
            data = data.encode('utf-8')
            req = urllib.request.Request(url, data)
            with urllib.request.urlopen(req) as f:
                response = f.read()
                convertname = response.decode('utf-8')
                print(convertname)
                convertname = convertname.replace('\n', '').replace('\r', '')
                #print(convertname)
                corresponding_geneID.append(convertname[14:])

    elif len(proteinlist) < 5:
        for i in range(len(proteinlist)):
            params = {
            'from': 'ACC+ID',
            'to': 'ENSEMBLGENOME_ID',#P_ENTREZGENEID,P_REFSEQ_AC,REFSEQ_NT_ID
            'format': 'tab',
            'query': proteinlist[i]
            }
            data = urllib.parse.urlencode(params)
            data = data.encode('utf-8')
            req = urllib.request.Request(url, data) 
            with urllib.request.urlopen(req) as f:
                response = f.read()
                convertname = response.decode('utf-8')
                print(convertname[14:])
                convertname = convertname.replace('\n', '').replace('\r', '')
                corresponding_geneID.append(convertname[14:])
 
    hit = list(zip(proteinlist, e_valuelist, score_bits, per_identity, corresponding_geneID,  descri_word))
    return hit
