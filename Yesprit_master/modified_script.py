import os
import sys
import re
import subprocess
import urllib.parse
import urllib.request
import time
import datetime
url = 'https://www.uniprot.org/uploadlists/'

#with open('records.txt','w') as Rf:
#    Rf.write( __file__+'\n')
#    Rf.write(os.path.realpath(__file__)+'\n')
#    Rf.write(sys.executable+'\n')
#    Rf.write(os.path.realpath(sys.executable)+'\n')
#    Rf.write(sys.argv[0]+'\n')
#    Rf.write(os.path.realpath(sys.argv[0])+'\n')
#    Rf.write(sys.path[0]+'\n')
#    Rf.write(os.path.realpath(sys.path[0])+'\n')
#Rf.close()

this_dir, this_filename = os.path.split(__file__)
IDPath = os.path.join(this_dir,'resources','IDs.txt')
#PFastPath = os.path.join(this_dir,'data','P','Pombe.fasta')
PFastPath = os.path.join(this_dir,'resources','4species.fasta')
SeqPath = os.path.join(this_dir,'resources','sequence.fasta')
BlaPath = os.path.join(this_dir,'resources','blastp_out.txt')


f1 = open(PFastPath,'r').readlines()
# f2 = open('new.fasta','w')
fadict={}
for i in f1:
    if i.startswith('>'):
        k = i.strip("\n").split('|')
        id = k[1]
        fa=''
    else:
        fa = fa + i.strip("\n")
        fadict[id]=fa
# for i in a:
#     f2.write(i+'\n'+a[i]+'\n')
# f2.close()

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
    #print(keywords)
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
    # cmd = 'blastp.exe -task blastp -query sequence.fasta -db {} -out blastp_out.txt'.format(dbPath)
    # cmd = 'blastp.exe -task blastp -query sequence.fasta -db japonicus.fasta -out blastp_out.txt'
    #print(cmd)
    os.popen(cmd)
    time.sleep(3)
    f.close()
    with open(BlaPath,'r') as f:
        #startime2=datetime.datetime.now()
        #print(startime2)
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
                #x = i.strip(' \n').split(' ')
                #print(x)
                extract_evalue = i.strip(' \n').split(' ')[-1]
                e_valuelist.append(extract_evalue)
                score = i.strip(' \n').split(' ')[-5]
                score_bits.append(score)
            elif 'Identities' in i:
                iden = re.split(r'[()]',i)[1]
                per_identity.append(iden)       
        #print(e_valuelist)
    f.close()
    #return proteinlist
    #['B6JWH1', 'B6K374', 'B6K4N7', 'B6K375', 'B6K4G0', 'B6JYB2', 'B6K5I6', 'B6JYH2', 'B6K1G8', 'B6JYD8']
    corresponding_geneID = []
#    searching_geneID = []
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

#            paramse = {
#            'from': 'ACC+ID',
#            'to': 'P_REFSEQ_AC',#P_ENTREZGENEID, REFSEQ_NT_ID
#            'format': 'tab',
#            'query': proteinlist[i]
#            }
#            data = urllib.parse.urlencode(paramse)
#            data = data.encode('utf-8')
#            req = urllib.request.Request(url, data)
#            with urllib.request.urlopen(req) as f:
#                response = f.read()
#                convertname1 = response.decode('utf-8')
#                convertname1 = convertname1.replace('\n', '').replace('\r', '')
##                print(convertname1)
#                searching_geneID.append(convertname1[14:])
##                print(searching_geneID)
        
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
                #print(convertname[14:])
                corresponding_geneID.append(convertname[14:])
                #print(corresponding_geneID)
#            paramse = {
#            'from': 'ACC+ID',
#            'to': 'P_REFSEQ_AC',#P_ENTREZGENEID, REFSEQ_NT_ID
#            'format': 'tab',
#            'query': proteinlist[i]
#            }
#            data = urllib.parse.urlencode(paramse)
#            data = data.encode('utf-8')
#            req = urllib.request.Request(url, data)
#            with urllib.request.urlopen(req) as f:
#                response = f.read()
#                convertname1 = response.decode('utf-8')
#                convertname1 = convertname1.replace('\n', '').replace('\r', '')
#                #print(convertname[14:])
#                searching_geneID.append(convertname1[14:])
        
    # hit = [evalue, score, ident,geneID]
    hit = list(zip(proteinlist, e_valuelist, score_bits, per_identity, corresponding_geneID,  descri_word))
    #print("p2g ID",datetime.datetime.now())
    # FinalResult.append(hit)
    # print(hit)
    # print(FinalResult)
    # return FinalResult
    #return proteinlist
    return hit
