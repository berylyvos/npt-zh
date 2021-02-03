import os
import math
from pypinyin import lazy_pinyin, Style
import pronouncing as pr
from Phyme import Phyme
ph = Phyme()

PERFECT, ASSONANCE, CONSONANT = 1, 2, 3
strip_chars = '\n .,;()[]<>-?!":*#。，；？！…—“”‘’：【】《》、'

def is_rhyming(w1, w2):
    if w1 == w2:
        return False
    try:
        if pr.phones_for_word(w1) == [] or pr.phones_for_word(w2) == []:
            return False
        sy = pr.syllable_count(pr.phones_for_word(w1)[0])
        if  sy in ph.get_perfect_rhymes(w2).keys() and w1 in ph.get_perfect_rhymes(w2)[sy]:
            return PERFECT
        # 半韵
        if sy in ph.get_assonance_rhymes(w2).keys() and w1 in ph.get_assonance_rhymes(w2)[sy]: 
            return ASSONANCE
        # 辅音韵
        if sy in ph.get_consonant_rhymes(w2).keys() and w1 in ph.get_consonant_rhymes(w2)[sy]: 
            return CONSONANT
    except:
        print('ERROR rhyming with ', w1, w2)
    return False

def _is_rhyming(w1, w2):
    return w1 in pr.rhymes(w2)

def reset_last_word(pw, lw):
    if lw == 're':
        return 'are', 1
    if lw == 'm':
        return 'am', 1
    if lw == 't':
        return pw+"'t", 2
    if lw == 's':
        return pw+"'s", 2
    if lw == 'd':
        return pw+"'d", 2

def strip_token(text):
    words = [word.strip(strip_chars) for word in text.split() if word.strip(strip_chars)]
    return ' '.join(words)

def count_zh_token(text):
    words = [word.strip(strip_chars) for word in text if word.strip(strip_chars)]
    return len(words)

def count_en_syllable(text):
    phones = [pr.phones_for_word(p)[0] for p in strip_token(text).split() if pr.phones_for_word(p)]
    return sum([pr.syllable_count(p) for p in phones])

def compute_rhyming_score(w1, w2, lv):
    penalty = [0.3, 0.5, 0.75]
    s1, s2 = [], []
    for enn in en[w1[1]]:
        if enn[0].split()[-1] == w1[0]:
            s1.append(enn[1])
    for enn in en[w2[1]]:
        if enn[0].split()[-1] == w2[0]:
            s2.append(enn[1])
    if len(s1) == 0 or len(s2) == 0:
        print(w1, w2)
        return 404
    return (sum(s1) / len(s1) + sum(s2) / len(s2))*penalty[lv-1]


root_dir = './top-10/'
out_dir = './out-top10/'
out_list, zh, en = [], [], []

def get_zh_rhyme():
    zh_rhyme, _d = [], dict()
    for i, z in enumerate(zh):
        _zz = z[-1]
        py = lazy_pinyin(_zz, style=Style.FINALS)[0]
        if py not in _d:
            _d[py] = [(_zz, i)]
        else:
            if _zz not in list(map(lambda x: x[0], _d[py])):
                _d[py].append((_zz, i))
    for dd in _d.values():
        if len(dd) > 1:
            zh_rhyme.append(dd)
    print('zh_rhyme: ', zh_rhyme)
    out_list.append('zh_rhyme: '+str(zh_rhyme))
    return zh_rhyme

def get_en_rhyme(zh_rhyme):
    rhy_table = []
    word_set_list = []
    for _zh_rhyme in zh_rhyme:
        word_set = set()
        for i, enn in enumerate(en):
            if i not in list(map(lambda x: x[1], _zh_rhyme)):
                continue
            for j, ennn in enumerate(enn):
                es = ennn[0].split()
                if es[-1] in ['m', 't', 's', 'd', 're'] and len(es)>1:
                    last_word, cd = reset_last_word(es[-2], es[-1])
                    enn[j][0] = " ".join(enn[j][0].split()[:-cd]) + " " +last_word
                else:
                    last_word = es[-1]
                word_set.add((last_word, i))
        word_set_list.append(word_set)

    for ws in word_set_list:
        word_lst = list(ws)
        for i, w1 in enumerate(word_lst):
            for w2 in word_lst[i+1:]:
                if w1[1] == w2[1]:
                    continue
                res = is_rhyming(w1[0], w2[0])
                if res > 0:
                    sc = compute_rhyming_score(w1, w2, res)
                    rhy_table.append((w1, w2, res, sc))
    
    rhy_table = sorted(rhy_table, key=lambda x: x[3])
    
    print('en_rhyme: ', rhy_table)
    out_list.append('en_rhyme: '+str(rhy_table))
    return rhy_table

def fill_rhyme(zh_rhyme, rhy_table):
    rhy_pos = dict()
    for _zr in zh_rhyme:
        for _zrr in _zr:
            rhy_pos[_zrr[1]] = None
    for rhy in rhy_table:
        r1, r2, lv, sc = rhy
        rhy_level = '$' + str(lv)
        if rhy_pos[r1[1]] == None and rhy_pos[r2[1]] == None:
            rhy_pos[r1[1]] = r1[0] + rhy_level
            rhy_pos[r2[1]] = r2[0] + rhy_level

    print('rhyme_pos: ', rhy_pos)
    out_list.append('rhyme_pos: '+str(rhy_pos))
    return rhy_pos

def out_to_file(rhy_pos, fn):
    out_en = ['']*len(en)
    for k, v in rhy_pos.items():
        if v != None:
            for enn in en[k]:
                if enn[0].split()[-1] == v.split('$')[0]:
                    out_en[k] = enn[0] + ' ' + (4-int(v.split('$')[1]))*'*'
                    break
    for i, z in enumerate(zh):
        cz = count_zh_token(z)
        print('#{} {} ({})'.format(i, z, cz))
        out_list.append('#'+str(i)+' '+z+' ('+str(cz)+')')
        if out_en[i] == '':
            print(en[i][0][0] + ' ('+str(count_en_syllable(en[i][0][0]))+')')
            out_list.append(en[i][0][0] + ' ('+str(count_en_syllable(en[i][0][0]))+')')
        else:
            ce = count_en_syllable(out_en[i])
            print(out_en[i] + ' ('+str(ce)+')')
            out_list.append(out_en[i]+ ' ('+str(ce)+')')
    with open(out_dir+fn, 'w') as otf:
        otf.write('\n'.join(out_list))

def syllable_filter():
    for i, z in enumerate(zh):
            c1 = count_zh_token(z)
            for k, enn in enumerate(en[i]):
                c2 = count_en_syllable(enn)
                en[i][k]= [enn, 0.5*abs(c2-c1)+0.5*k]
            en[i] = sorted(en[i], key=lambda x: x[1])


if __name__ == '__main__':
    for fn in os.listdir(root_dir):
        if fn in os.listdir(out_dir):
            continue
        zh, en, out_list = [], [], []
        f = open(root_dir+fn, 'r')
        lines = f.readlines()
        for line in lines:
            if line.isspace():
                continue
            if ord(line[0]) > 127:
                zh.append(strip_token(line))
                enn = []
                en.append(enn)
            else:
                enn.append(strip_token(line))
        assert len(zh) == len(en)
        f.close()        
        
        syllable_filter()
        zh_rhyme = get_zh_rhyme()
        rhy_table = get_en_rhyme(zh_rhyme)
        rhy_pos = fill_rhyme(zh_rhyme, rhy_table)
        out_to_file(rhy_pos, fn)
        
