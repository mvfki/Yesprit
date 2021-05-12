import os.path
from sqlite3 import connect
from pickle import load
from urllib.error import URLError
from Bio.Blast.NCBIWWW import qblast
from subprocess import Popen, PIPE
import re
import urllib.parse
import urllib.request
import csv
url = 'https://www.uniprot.org/uploadlists/'

this_dir, this_filename = os.path.split(__file__)
namefile_path = os.path.join(this_dir,'resources','4species_name.csv')


def importGenome(species):
    dataPath = os.path.join(this_dir, 'data', species, 'seq.pkl')
    with open(dataPath, 'rb') as f:
        fasta = load(f)
    f.close()
    return fasta

def searchname(keyword,species):
    csv_file = csv.reader(open(namefile_path))
    for lines in csv_file:
        if keyword in lines:
            if keyword == lines[0] or keyword == lines[1]:
                if species == 'J':
                    keyword_ID = lines[4]
                    return keyword_ID
                elif species == 'O':
                    keyword_ID = lines[2]
                    return keyword_ID
                elif species == 'C':
                    keyword_ID = lines[3]
                    return keyword_ID
                elif species == 'P':
                    keyword_ID = keyword
                    return keyword_ID
        else:
             keyword_ID = keyword
    return keyword_ID

def searchAnno(species, keyword_search):
    '''
    Search the preprepared SQLite3 database for the given keywords, and return 
    the matched result.
    Arguments:
    ----------
    species - str. 
              Choose from {c}.
    keyword - str.
              Can be either GenBank accession ID, gene symbol, or systematic 
              ID (PomBase) for S. pombe. 
    Return:
    ----------
    result - list.
             elements are tuples with 9 fields each, where the 3rd is the 
             chromosome identifier, the 4th for the start, the 5th for the end, 
             the 6th for the strand. 
    '''
    keyword = searchname(keyword_search,species)
    dbPath = os.path.join(this_dir, 'data', species, 'ANNOTATION.db')
    conn = connect(dbPath)
    c = conn.cursor()
    cmd = '''SELECT * 
    FROM ANNOTATION
    WHERE GenBank = "{0}" 
    OR ID = "{0}" 
    OR PomBase LIKE "%{0}%"
    OR Symbol = "{0}";'''.format(keyword)
    results = c.execute(cmd).fetchall()
    conn.close()
    return results    

def locateCDS(species, chromosome, start, end):
    dbPath = os.path.join(this_dir, 'data', species, 'ANNOTATION.db')
    conn = connect(dbPath)
    c = conn.cursor()
    pos = sorted([start, end])
    start, end = pos[0], pos[1]
    cmd = '''SELECT GenBank, prod
    FROM ANNOTATION
    WHERE chromosome = "{}"
    AND start <= {}
    AND end >= {}'''.format(chromosome, start, end)
    results = c.execute(cmd).fetchall()
    conn.close()
    return results

# Basic string/sequence manipulation ######

def GC(primer):
    nGC = primer.count('G') + primer.count('C')
    return str(round(nGC / len(primer) * 100, 1))
    
def TM(primer):
    nGC = primer.count('G') + primer.count('C')
    TM = 69.897 + 0.41 * nGC / len(primer) * 100 - 600 / len(primer)
    return str(round(TM, 3))

def TM2(primer):
    nGC = primer.count('G') + primer.count('C')
    TM = 4 * nGC + 2 * (len(primer) - nGC)
    return str(round(TM, 1))

def antisense(sequence):
    seq_list = []
    RC = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G'}
    sequence = sequence.upper()
    seq_list = [RC[i] for i in sequence[::-1]]
    return ''.join(seq_list)

def _addSpacesUtilLen(string, fullLength):
    assert type(string) == str and type(fullLength) == int
    assert len(string) <= fullLength
    for i in range(fullLength - len(string)):
        string += ' '
    return string

def formatMultiResult(result):
    nResult = len(result)
    outString = ''
    maxC1, maxC2, maxC3 = 0, 0, 0
    for entry in result:
        maxC1 = max(maxC1, len(str(entry[6])))
        maxC2 = max(maxC2, len(str(entry[7])))
        maxC3 = max(maxC3, len(str(entry[8])))
    maxC1 = max(maxC1, 7) # 7 for "GenBank"
    maxC2 = max(maxC2, 13) # 13 for "Systematic ID"
    maxC3 = max(maxC3, 11) # 11 for "Gene Symbol"
    outString += _addSpacesUtilLen('GenBank', maxC1) + ' ' + \
                 _addSpacesUtilLen('Systematic ID', maxC2) + ' ' + \
                 _addSpacesUtilLen('Gene Symbol', maxC3) + '\n'
    for entry in result:
        outString += _addSpacesUtilLen(str(entry[6]), maxC1) + ' ' + \
                     _addSpacesUtilLen(str(entry[7]), maxC2) + ' ' + \
                     _addSpacesUtilLen(str(entry[8]), maxC3) + '\n'
    return nResult, outString

# Core Calculation ######

def get_del_primer(species, keyword, target_length):
    result = searchAnno(species, keyword)
    if len(result) != 1:
        return result
    else:
        position = list(result[0][2:6])
        position[1] -= 1
    chromosome_fa = importGenome(species)
    chromosome_seq = chromosome_fa[position[0]]
    print('>{} FASTA_format_CDS_sequence'.format(keyword))
    if position[3] == 1:
        print(chromosome_seq[position[1]:position[2]])
    else:
        print(antisense(chromosome_seq[position[1]:position[2]]))

    if position[3] == 1:
        forward_primer_start = position[1] - target_length
        forward_primer_end = position[1]
        reverse_primer_start = position[2]
        reverse_primer_end = position[2] + target_length
        forward_primer = chromosome_seq[forward_primer_start:forward_primer_end].upper()
        reverse_primer = antisense(chromosome_seq[reverse_primer_start:reverse_primer_end])
    elif position[3] == -1:
        reverse_primer_start = position[1] - target_length
        reverse_primer_end = position[1]


        forward_primer_start = position[2]
        forward_primer_end = position[2] + target_length
        reverse_primer = chromosome_seq[reverse_primer_start:reverse_primer_end].upper()
        forward_primer = antisense(chromosome_seq[forward_primer_start:forward_primer_end])

    return (forward_primer, reverse_primer, 
            (result[0][-1], result[0][-3], result[0][-2]))

def get_Ctag_primer(species, keyword, target_length):
    result = searchAnno(species, keyword)
    if len(result) != 1:
        return result
    else:
        position = list(result[0][2:6])
        position[1] -= 1
    chromosome_fa = importGenome(species)
    chromosome_seq = chromosome_fa[position[0]]
    print('>{} FASTA_format_CDS_sequence'.format(keyword))
    if position[3] == 1:
        print(chromosome_seq[position[1]:position[2]])
    else:
        print(antisense(chromosome_seq[position[1]:position[2]]))
    
    if position[3] == 1:
        forward_primer_start = position[2] - 3 - target_length
        forward_primer_end = position[2] - 3
        reverse_primer_start = position[2]
        reverse_primer_end = position[2] + target_length
        forward_primer = chromosome_seq[forward_primer_start:forward_primer_end].upper()
        reverse_primer = antisense(chromosome_seq[reverse_primer_start:reverse_primer_end])
    elif position[3] == -1:
        reverse_primer_start = position[1] - target_length
        reverse_primer_end = position[1]
        forward_primer_start = position[1] + 3
        forward_primer_end = position[1] + 3 + target_length
        reverse_primer = chromosome_seq[reverse_primer_start:reverse_primer_end].upper()
        forward_primer = antisense(chromosome_seq[forward_primer_start:forward_primer_end])

    return (forward_primer, reverse_primer, 
            (result[0][-1], result[0][-3], result[0][-2]))

def get_Ntag_none_primer(species, keyword, target_length):
    result = searchAnno(species, keyword)
    if len(result) != 1:
        return result
    else:
        position = list(result[0][2:6])
        position[1] -= 1
    chromosome_fa = importGenome(species)
    chromosome_seq = chromosome_fa[position[0]]
    print('>{} FASTA_format_CDS_sequence'.format(keyword))
    if position[3] == 1:
        print(chromosome_seq[position[1]:position[2]])
    else:
        print(antisense(chromosome_seq[position[1]:position[2]]))

    if position[3] == 1:
        forward_primer_start = position[1] - target_length
        forward_primer_end = position[1]
        reverse_primer_start = position[1] + 3
        reverse_primer_end = position[1] + 3 + target_length
        forward_primer = chromosome_seq[forward_primer_start:forward_primer_end].upper()
        reverse_primer = antisense(chromosome_seq[reverse_primer_start:reverse_primer_end])
    elif position[3] == -1:
        reverse_primer_start = position[2] - 3 - target_length
        reverse_primer_end = position[2] - 3
        forward_primer_start = position[2]
        forward_primer_end = position[2] + target_length
        reverse_primer = chromosome_seq[reverse_primer_start:reverse_primer_end].upper()
        forward_primer = antisense(chromosome_seq[forward_primer_start:forward_primer_end])
    
    return (forward_primer, reverse_primer, 
            (result[0][-1], result[0][-3], result[0][-2]))

def get_Ntag_tag_primer(species, keyword, target_length):
    result = searchAnno(species, keyword)
    if len(result) != 1:
        return result
    else:
        position = list(result[0][2:6])
        position[1] -= 1
    chromosome_fa = importGenome(species)
    chromosome_seq = chromosome_fa[position[0]]
    print('>{} FASTA_format_CDS_sequence'.format(keyword))
    if position[3] == 1:
        print(chromosome_seq[position[1]:position[2]])
    else:
        print(antisense(chromosome_seq[position[1]:position[2]]))

    if position[3] == 1:
        forward_primer_start = position[1] - target_length
        forward_primer_end = position[1]
        reverse_primer_start = position[1]
        reverse_primer_end = position[1] + target_length
        forward_primer = chromosome_seq[forward_primer_start:forward_primer_end].upper()
        reverse_primer = antisense(chromosome_seq[reverse_primer_start:reverse_primer_end])
    elif position[3] == -1:
        reverse_primer_start = position[2] - target_length
        reverse_primer_end = position[2]
        forward_primer_start = position[2]
        forward_primer_end = position[2] + target_length
        reverse_primer = chromosome_seq[reverse_primer_start:reverse_primer_end].upper()
        forward_primer = antisense(chromosome_seq[forward_primer_start:forward_primer_end])
    
    return (forward_primer, reverse_primer, 
            (result[0][-1], result[0][-3], result[0][-2]))

def callLocalBLAST(query, species, min_cov = 0.15, max_eval = 1):
    dbPath = os.path.join(this_dir, 'data', species, 'blastdb')
    blastPath = os.path.join(this_dir, 'lib', 'blastn.exe')
    cmd = [blastPath, '-query', '-', '-db', dbPath, '-word_size', '11', 
           '-reward', '2', '-penalty', '-3', '-gapopen', '5', '-gapextend', 
           '2', '-outfmt', '6', '-evalue', str(max_eval)]
    p = Popen(cmd, stdin = PIPE, stdout = PIPE)
    stdout = p.communicate(input = query)[0].decode()
    # Fields: query acc.ver, subject acc.ver, % identity, alignment length, 
    # mismatches, gap opens, q. start, q. end, s. start, s. end, evalue, bit 
    # score
    needed = []
    for line in stdout.splitlines():
        tokens = line.split('\t')
        if int(tokens[3])/len(query) >= min_cov:
            needed.append(tokens)
    return needed

def BLAST_by_sp(keyword, species, min_cov, max_eval):
    # Get the query sequence
    result = searchAnno('P', keyword)
    if len(result) != 1:
        return 'NoName'
    else:
        position = list(result[0][2:6])
        position[1] -= 1
    chromosome_fa = importGenome('P')
    chromosome_seq = chromosome_fa[position[0]]
    if position[3] == 1:
        query = chromosome_seq[position[1]:position[2]].upper()
    else:
        query = antisense(chromosome_seq[position[1]:position[2]])
    # Call local BLAST against target species
    topHits = callLocalBLAST(query.encode(), species, min_cov = min_cov, max_eval = max_eval)
    FinalResult = []
    for tokens in topHits:
        chromosome, start, end = tokens[1], int(tokens[8]), int(tokens[9])
        ident, evalue, cov = float(tokens[2]), float(tokens[10]), int(tokens[3])
        cov /= len(query)
        cov *= 100
        hit = [evalue, cov, ident]
        genbankIDs = locateCDS(species, chromosome, start, end)
        for i in genbankIDs:
            hitappend(i)
        FinalResult.append(hit)

    return FinalResult

def get_check_primer_range(species, gene_name, target_length, 
                           mode, Ntag, scale):
    result = searchAnno(species, gene_name)
    if len(result) != 1:
        return result
    else:
        position = list(result[0][2:6])
        position[1] -= 1
    chromosome_fa = importGenome(species)
    chromosome_seq = chromosome_fa[position[0]]

    if mode == 'del':
        if position[3] == 1:
            forward_primer_start = position[1] - target_length
            forward_range_start = position[1] - scale
            reverse_primer_end = position[2] + target_length
            reverse_range_end = position[2] + scale
        else:
            reverse_primer_start = position[1] - target_length
            reverse_range_start = position[1] - scale
            forward_primer_end = position[2] + target_length
            forward_range_end = position[2] + scale
    elif mode == 'C':
        if position[3] == 1:
            forward_primer_start = position[2] - 3 - target_length
            forward_range_start = position[2] - 3 - scale
            reverse_primer_end = position[2] + target_length
            reverse_range_end = position[2] + scale
        else:
            reverse_primer_start = position[1] - target_length
            reverse_range_start = position[1] - scale
            forward_primer_end = position[1] + 3 + target_length
            forward_range_end = position[1] + 3 + scale
    elif mode=='N':
        if Ntag == ' ':
            if position[3] == 1:
                forward_primer_start = position[1] - target_length
                forward_range_start = position[1] - scale
                reverse_primer_end = position[1] + 3 + target_length
                reverse_range_end = position[1] + 3 + scale
            else:
                reverse_primer_start = position[2] - 3 - target_length
                reverse_range_start = position[2] - 3 - scale
                forward_primer_end = position[2] + target_length
                forward_range_end = position[2] + scale
        else:
            if position[3] == 1:
                forward_primer_start = position[1] - target_length
                forward_range_start = position[1] - scale
                reverse_primer_end = position[1] + target_length
                reverse_range_end = position[1] + scale
            else:
                reverse_primer_start = position[2] - target_length
                reverse_range_start = position[2] - scale
                forward_primer_end = position[2] + target_length
                forward_range_end = position[2] + scale
    if position[3] == 1:
        search_rangeL = chromosome_seq[forward_range_start:forward_primer_start].upper()
        search_rangeR = chromosome_seq[reverse_primer_end:reverse_range_end].upper()
    else:
        search_rangeR = chromosome_seq[forward_primer_end:forward_range_end].upper()
        search_rangeL = chromosome_seq[reverse_range_start:reverse_primer_start].upper()
    return search_rangeL, search_rangeR

def get_check_primer(search_rangeL, search_rangeR, length, 
                     GCmin, GCmax, TMopt, TMmin, TMmax):
    index_list = []
    for i in range(len(search_rangeL)):
        if i + length + 1 > len(search_rangeL):
            break
        if search_rangeL[i] == 'C' or search_rangeL[i] == 'G':
            index_list.append(i)
    wait2check = []
    for i in index_list[::-1]:
        subs_1 = search_rangeL[i:i + length]
        GCcontent = float(GC(subs_1))
        TM = float(TM2(subs_1))
        if TM == TMopt:
            sub1 = subs_1
            break
        elif TM <= TMmax and TM >= TMmin and GCcontent <= GCmax and GCcontent >= GCmin:
            wait2check.append(subs_1)
    try:
        subs1 = sub1
    except ValueError:
        subs1 = wait2check[0]

    index_list = []
    for i in range(len(search_rangeR)):
        if i + length>len(search_rangeL):
            break
        if search_rangeR[i] == 'C' or search_rangeR[i] == 'G':
            index_list.append(i)
    wait2check = []
    for i in index_list:
        subs_2 = search_rangeR[i:i + length]
        GCcontent = float(GC(subs_2))
        TM = float(TM2(subs_2))
        if TM == TMopt:
            sub2 = subs_2
            break
        elif TM <= TMmax and TM >= TMmin and GCcontent <= GCmax and GCcontent >= GCmin:
            wait2check.append(subs_2)
    try:
        subs2 = antisense(sub2)
    except ValueError:
        subs2 = antisense(wait2check[0])
    return subs1, subs2
