import re
import logging

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')

TYPES = []

# List of possible language templates and their corresponding cleaned versions.
LANG_TEMPLATES = [['ab', '(ab)'], ['ace', '(ace)'], ['ach', '(ach)'], ['ady', '(ady)'], ['aa', '(aa)'], ['af', '(af)'], ['sq', '(sq)'], ['de', '(de)'], ['pdc', '(pdc)'], ['gsw', '(gsw)'], ['zgh', '(zgh)'], ['am', '(am)'], ['en', '(en)'], ['en-us', '(en-US)'], ['en-gb', '(en-GB)'], ['simple', '(simple)'], ['ar', '(ar)'], ['Ar-Latn', '(ar-Latn)'], ['arz', '(arz)'], ['ary', '(ary)'], ['aeb', '(aeb)'], ['an', '(an)'], ['hy', '(hy)'], ['rup', '(rup)'], ['as', '(as)'], ['ast', '(ast)'], ['atj', '(atj)'], ['ae', '(ae)'], ['ay', '(ay)'], ['az', '(az)'], ['ba', '(ba)'], ['bm', '(bm)'], ['map-bms', '(map-bms)'], ['nds', '(nds)'], ['nds-nl', '(nds-NL)'], ['eu', '(eu)'], ['bar', '(bar)'], ['bia', '(bia)'], ['bn', '(bn)'], ['bi', '(bi)'], ['bcl', '(bcl)'], ['be', '(be)'], ['be-tarask', '(be-tarask)'], ['bh', '(bh)'], ['my', '(my)'], ['bpy', '(bpy)'], ['lang:nb', '(nb)'], ['bs', '(bs)'], ['Bua', '(bua)'], ['bxu', '(bxu)'], ['bxm', '(bxm)'], ['bxr', '(bxr)'], ['br', '(br)'], ['bg', '(bg)'], ['ks', '(ks)'], ['yue', '(yue)'], ['osp', '(osp)'], ['ca', '(ca)'], ['ceb', '(ceb)'], ['ch', '(ch)'], ['shy', '(shy)'], ['cbk', '(cbk)'], ['ny', '(ny)'], ['zh', '(zh)'], ['lzh', '(lzh)'], ['zh-hans', '(zh-Hans)'], ['zh-hant', '(zh-Hant)'], ['zh-cn', '(zh-CN)'], ['zh-hk', '(zh-HK)'], ['zh-mo', '(zh-MO)'], ['zh-sg', '(zh-SG)'], ['zh-tw', '(zh-TW)'], ['si', '(si)'], ['kw', '(kw)'], ['co', '(co)'], ['ko', '(ko)'], ['mus', '(mus)'], ['kea', '(kea)'], ['gcf', '(gcf)'], ['ht', '(ht)'], ['lou', '(lou)'], ['crs', '(crs)'], ['cpf', '(cpf)'], ['cr', '(cr)'], ['hr', '(hr)'], ['dak', '(dak)'], ['uhn', '(uhn)'], ['da', '(da)'], ['prs', '(prs)'], ['dta', '(dta)'], ['dyu', '(dyu)'], ['dz', '(dz)'], ['myv', '(myv)'], ['es', '(es)'], ['eo', '(eo)'], ['et', '(et)'], ['Ekk', '(ekk)'], ['ext', '(ext)'], ['eto', '(eto)'], ['ee', '(ee)'], ['fo', '(fo)'], ['fj', '(fj)'], ['fil', '(fil)'], ['fi', '(fi)'], ['vls', '(vls)'], ['fr', '(fr)'], ['fr1835', '(fr1835)'], ['frm', '(frm)'], ['fro', '(fro)'], ['fr-be', '(fr-BE)'], ['frp', '(frp)'], ['fur', '(fur)'], ['fy', '(fy)'], ['gag', '(gag)'], ['gd', '(gd)'], ['gl', '(gl)'], ['fra-gal', '(fra-gal)'], ['cy', '(cy)'], ['gil', '(gil)'], ['got', '(got)'], ['grc', '(grc)'], ['el', '(el)'], ['pnt', '(pnt)'], ['kl', '(kl)'], ['gn', '(gn)'], ['gez', '(gez)'], ['gu', '(gu)'], ['ka', '(ka)'], ['hak', '(hak)'], ['ha', '(ha)'], ['mey', '(mey)'], ['hsb', '(hsb)'], ['haw', '(haw)'], ['he', '(he)'], ['hz', '(hz)'], ['hi', '(hi)'], ['hif', '(hif)'], ['hu', '(hu)'], ['io', '(io)'], ['ig', '(ig)'], ['ilo', '(ilo)'], ['id', '(id)'], ['ia', '(ia)'], ['ie', '(ie)'], ['iu', '(iu)'], ['ik', '(ik)'], ['ga', '(ga)'], ['is', '(is)'], ['it', '(it)'], ['ja', '(ja)'], ['ja-Latn', '(ja-Latn)'], ['jv', '(jv)'], ['nrf', '(nrf)'], ['tmr', '(tmr)'], ['lad', '(lad)'], ['kbd', '(kbd)'], ['kab', '(kab)'], ['kn', '(kn)'], ['kaa', '(kaa)'], ['kk', '(kk)'], ['kk-Arab', '(kk-Arab)'], ['kk-Cyrl', '(kk-Cyrl)'], ['kk-Latn', '(kk-Latn)'], ['km', '(km)'], ['naq', '(naq)'], ['kg', '(kg)'], ['ki', '(ki)'], ['rw', '(rw)'], ['ky', '(ky)'], ['run', '(run)'], ['ksh', '(ksh)'], ['ku', '(ku)'], ['kmr', '(kmr)'], ['lld', '(lld)'], ['lo', '(lo)'], ['la', '(la)'], ['lv', '(lv)'], ['li', '(li)'], ['ln', '(ln)'], ['lt', '(lt)'], ['lob', '(lob)'], ['lmo', '(lmo)'], ['lua', '(lua)'], ['luo', '(luo)'], ['lb', '(lb)'], ['mk', '(mk)'], ['mk-Cyrl', '(mk-Cyrl)'], ['mk-Latn', '(mk-Latn)'], ['ms', '(ms)'], ['xmm', '(xmm)'], ['ml', '(ml)'], ['mg', '(mg)'], ['mt', '(mt)'], ['dv', '(dv)'], ['Cmn', '(cmn)'], ['mnc', '(mnc)'], ['gv', '(gv)'], ['lang:mi', '(mi)'], ['rar', '(rar)'], ['lang:mr', '(mr)'], ['mhr', '(mhr)'], ['mrq', '(mrq)'], ['mqm', '(mqm)'], ['mh', '(mh)'], ['nan', '(nan)'], ['mwl', '(mwl)'], ['moh', '(moh)'], ['mo', '(ro)'], ['mn', '(mn)'], ['mn-Cyrl', '(mn-Cyrl)'], ['mn-Latn', '(mn-Latn)'], ['mn-Mong', '(mn-Mong)'], ['mvf', '(mvf)'], ['cnr', '(cnr)'], ['cnr-Cyrl', '(cnr-Cyrl)'], ['cnr-Latn', '(cnr-Latn)'], ['mug', '(mug)'], ['mga', '(mga)'], ['nah', '(nah)'], ['nap', '(nap)'], ['na', '(na)'], ['nv', '(nv)'], ['nd', '(nd)'], ['nr', '(nr)'], ['nl', '(nl)'], ['nl-be', '(nl-BE)'], ['ne', '(ne)'], ['new', '(new)'], ['niu', '(niu)'], ['fra-nor', '(fra-nor)'], ['no', '(no)'], ['nn', '(nn)'], ['oc', '(oc)'], ['or', '(or)'], ['om', '(om)'], ['os', '(os)'], ['ug', '(ug)'], ['ur', '(ur)'], ['uz', '(uz)'], ['ps', '(ps)'], ['pi', '(pi)'], ['pau', '(pau)'], ['pam', '(pam)'], ['pap', '(pap)'], ['prk', '(prk)'], ['pa', '(pa)'], ['fa', '(fa)'], ['ff', '(ff)'], ['fil', '(fil)'], ['pcd', '(pcd)'], ['pms', '(pms)'], ['pl', '(pl)'], ['pt', '(pt)'], ['pt-br', '(pt-BR)'], ['qu', '(qu)'], ['rap', '(rap)'], ['rm', '(rm)'], ['rmy', '(rmy)'], ['ro', '(ro)'], ['ru', '(ru)'], ['ru-Latn', '(ru-Latn)'], ['rue', '(rue)'], ['orv-olr', '(orv-olr)'], ['slr', '(slr)'], ['smi', '(smi)'], ['se', '(se)'], ['sm', '(sm)'], ['sgs', '(sgs)'], ['sg', '(sg)'], ['sa', '(sa)'], ['sc', '(sc)'], ['sco', '(sco)'], ['sr', '(sr)'], ['sh', '(sh)'], ['sn', '(sn)'], ['scn', '(scn)'], ['szl', '(szl)'], ['sd', '(sd)'], ['sk', '(sk)'], ['sl', '(sl)'], ['so', '(so)'], ['snk', '(snk)'], ['ckb', '(ckb)'], ['nso', '(nso)'], ['st', '(st)'], ['su', '(su)'], ['sv', '(sv)'], ['gsw-ch', '(gsw-CH)'], ['sw', '(sw)'], ['syr', '(syr)'], ['tg', '(tg)'], ['tl', '(tl)'], ['ty', '(ty)'], ['ber', '(ber)'], ['ta', '(ta)'], ['tt', '(tt)'], ['crh', '(crh)'], ['tsg', '(tsg)'], ['cv', '(cv)'], ['cs', '(cs)'], ['ce', '(ce)'], ['te', '(te)'], ['tet', '(tet)'], ['th', '(th)'], ['bo', '(bo)'], ['ti', '(ti)'], ['tpi', '(tpi)'], ['tokipona', '(tokipona)'], ['to', '(to)'], ['als', '(als)'], ['tyv', '(tyv)'], ['ts', '(ts)'], ['tn', '(tn)'], ['tr', '(tr)'], ['ota', '(ota)'], ['tk', '(tk)'], ['tvl', '(tvl)'], ['tw', '(tw)'], ['uk', '(uk)'], ['lang:ve', '(ve)'], ['vec', '(vec)'], ['ang', '(ang)'], ['sga', '(sga)'], ['vi', '(vi)'], ['lang:non', '(non)'], ['otk', '(otk)'], ['vo', '(vo)'], ['vro', '(vro)'], ['wls', '(wls)'], ['wa', '(wa)'], ['war', '(war)'], ['woe', '(woe)'], ['wo', '(wo)'], ['wuu', '(wuu)'], ['xh', '(xh)'], ['sjo', '(sjo)'], ['yak', '(yak)'], ['ii', '(ii)'], ['yi', '(yi)'], ['yo', '(yo)'], ['zza', '(zza)'], ['zea', '(zea)'], ['za', '(za)'], ['zu', '(zu)']]


def get_template_type(template: str):
    """
    Takes a string of the whole template (except for: {{ }}) and returns either the cleaned version of the template or the same template if cleaning fails.
    """
    # Deal with {{date}} templates
    match = re.match(r"([Dd]ate-?)( de naissance)? ?", template)
    if match:
        _, i = match.span()
        result=  get_date(template, i)
        return result
    
    # ((([0-9]+)|([IVXL]+))es?)|((1|I)(er|re|e)s?)|(es?)|(èmes?) ?
    match = re.match(r"((([0-9]+)|([IVXL]+))es?)|((1|I)(er|re|e)s?)|(es?(?<=$))|(èmes?) ?", template)
    if match:
        _, i = match.span()
        result=  get_nbe(template, i)
        return result
    
    # Formatnum
    match = re.match(r"([fF]ormatnum ?: ?[0-9.,]+) ?", template)
    if match:
        result = get_num(template)
        return result
    
    # Siècles modèles 1
    match = re.match(r"-?[sS]([Aa][vp])?-?( [Mm]ini-?)? ?\|", template)
    if match:
        _, i = match.span()
        result = get_siècle(template, i)
        return result
    
    # Siècles modèles 2
    match = re.match(r"-?[sS](2|p)-? ?\|", template)
    if match:
        _, i = match.span()
        result = get_siècles(template, i)
        return result
    
    # Heures
    match = re.match(r"[hH]eures? ?\|", template)
    if match:
        _, i = match.span()
        result = get_heures(template, i)
        return result
    
    # Unité
    match = re.match(r"(([Uu]nité(/2)?)|([Nn]b)|([Nn]ombre)|([Nn]obr)|([Nn]obr [Rr]omains?)) ?\|", template)
    if match:
        _, i = match.span()
        result = get_unité(template, i)
        return result
    
    # Diverses templates
    match = re.match(r"([Nn]°)|([Nn]uméros?)|(p\.)|([vV]ol\.)|(§) ?\|?", template)
    if match:
        _, i = match.span()
        result = get_div(template, i)
        return result
    
    # Other matches:
    match = re.match(r"[aA]v JC ?", template)
    if match:
        return "av. J.-C. "
    
    # Incise
    match = re.match(r"[Ii]ncise ?\|", template)
    if match:
        _, i = match.span()
        result = get_incise(template, i)
        return result
    
    # Langue
    match = re.match(r"[Ll]ang((ue)|(-.{1,4}))?.*?\|", template)
    if match:
        _, i = match.span()
        result = get_lang(template, i)
        return result
    
    # Citation
    match = re.match(r"[Cc]ita(tion)? ?( étrangère)?( bloc)? ?\|", template)
    if not match:
        match = re.match(r"(([Dd]ébut)|([Ff]in))  ?[Cc]ita(tion)?", template)
    if match:
        _, i = match.span()
        result = get_cita(template, i)
        return result
    
    # Nb romains
    result = get_nb_rom(template)
    if result:
        return result
    
    # dealing with template {{,}}
    if template == ",":
        return ""
    
    # Liens et notes
    match = re.match(r"(([Ll]ien (web)|(brisé))|([Nn]otes?)|([Aa]rticles?)) ?\|", template)
    if match:
        return ""
    
    for lang in LANG_TEMPLATES:
        if lang[0] == template:
            return lang[1]
    return r"{{}}"


def get_nb_rom(template_word):
    nb_romains = "IVXL"
    match = True
    for char in template_word:
        if not char in nb_romains:
            match = False
    if match:
        return template_word
    return False


def get_date(template_word, i):
    result = ""
    word = ""
    for char in template_word[i:]:
        if not char == "|":
            word += char
        else:
            if not "=" in word:
                result += word + " "
            word = ""
    if not "=" in word:
        result += word

    return result


def get_nbe(template_word, i):
    result = ""
    word = ""
    for char in template_word:
        if not char == "|":
            result += char
        else:
            if not "=" in word:
                result += word + " "
            word = ""
    if not "=" in word:
        result += word
    if result[-2:] == " s":
        return result[:-2]
    return result


def get_num(template_word):
    result = ""
    word = ""
    if "formatnum:" == template_word[:10]:
        result = template_word[10:]
        return result
    return ""


def get_siècle(template_word, i):
    tag = template_word[:i]
    siècle = template_word[i:]
    siècle = get_e_ou_er([siècle])[0]

    if not " mini" in tag:
        siècle += " siècle"
        if tag[0] == "-":
            siècle += " av. J.-C."
        elif "sap" in tag:
            siècle += " apr. J.-C."

    return siècle


def get_siècles(template_word, i):
    tag = template_word[:i]
    param = template_word[i:]
    result = ""
    dates = []
    word = ""

    if "s2" in tag:
        for char in param:
            if char == "|":
                dates.append(word)
                word = ""
            else:
                word += char
        dates.append(word)
        d = get_e_ou_er(dates)

        if len(d) > 1:
            result = d[0] + " et " + d[1] + " siècles"
        else:
            logging.debug("Error in date format in templates: couldn't find two dates")
    
    elif "sp" in tag:
        for char in param:
            if char == "|":
                dates.append(word)
                word = ""
            else:
                word += char
        dates.append(word)
        
        if len(dates) >= 3:
            dates_rom = get_e_ou_er([dates[0], dates[2]])
            date1, date2 = dates_rom[0], dates_rom[1]

            result = date1
            if dates[1] == "ou":
                result += " ou " + date2

            elif dates[1] == "au":
                result += " au " + date2
            elif dates[1] == "-":
                result = date1 + " - " + date2
            
            result += " siècle"
            
            if dates[-1] == "s":
                result += "s"

    if tag[0] == "-":
        result += " av. J.-C."
    return result


def get_e_ou_er(dates):
    r = []
    for date in dates:
        if date == "I":
            date += "er"
            r.append(date)
        else: 
            date += "e"
            r.append(date)
    return r


def get_heures(template_word, i):
    values = []
    result = ""
    word = ""

    for char in template_word[i:]:
        if char == "|":
            if not "=" in word:
                values.append(word)
            word = ""
        else:
            word += char
    if not "=" in word:
        values.append(word)

    time_stamps = ["h", "min", "s"]
    for i in range(len(values)):
        if values[i]:
            try:
                ts = time_stamps[i]
            except IndexError:
                ts = ""
            result += values[i] + " " + ts + " "
    
    return result[:-1]


def get_unité(template_word, i):
    result = ""
    word = ""
    for char in template_word[i:]:
        if char == "|":
            if not "=" in word:
                result += word + " "
            word = ""
        else:
            word += char
    if not "=" in word:
        result += word
    return result


def get_div(template_word, i):
    result = ""

    for char in template_word:
        if not char == "|":
            result += char
        else:
            result += " "

    return result


def get_incise(template_word, i):
    word = ""
    # param2 = False
    for char in template_word[i:]:
        if not char == "|":
            word += char
        else:
            # param2 = True
            return "— " + word

    return "— " + word + " —"


def get_lang(template_word, i):
    result = ""
    tag = template_word[:i].lower()
    if tag == "langue|" or tag == "lang|":
        param0 = True
        param = False
        param2 = False
        param3 = False
        p0 = ""
        p1 = ""
        p2 = ""
        p3 = ""
        for char in template_word[i:]:
            if char == "|":
                if not param:
                    param = True
                elif not param2:
                    param2 = True
                elif not param3:
                    param3 = True
            elif param3:
                p3 += char
            elif param2:
                p2 += char
            elif param:
                p1 += char
            elif param0:
                p0 += char

        if p0 == "rtl" or p0 == "ltr":
            result = p2
        else:
            result = p1
        if p2:
            if "trans=" in p2:
                result += " (" + p2[6:] + ")"

    elif "-" in tag:
        for char in template_word[i:]:
            result += char

    if "texte=" in result:
        return result[6:]

    return result


def get_cita(template_word, i):
    tag = template_word[:i]
    result = ""
    if "début" in tag.lower():
        return "« "
    elif "fin" in tag.lower():
        return " »"

    if "étrangère" in tag:
        seq1 = ""
        seq2 = ""
        s2 = False
        for char in template_word[i:]:
            if char == "|":
                if s2 == True:
                    break
                s2 = True
            else:
                if s2:
                    seq2 += char
                else:
                    seq1 += char
        if "lang" in seq1 and "=" in seq1:
            result += seq2
        else:
            result += seq1
    else:
        for char in template_word[i:]:
            if not char == "|":
                result += char
            else:
                break

    if "bloc" in tag:
        return "\n« " + result +" »"
    return "« " + result + " »"


def remove_templates(content):
    """
    Takes a string and cleans the french wiki templates if possible. If not, will return empty doubble curly braces ("{{}}").
    """
    if not isinstance(content, str):
        return content
    result = ""
    matches = re.finditer(r"\{\{[^\n{]*?\}\}", content)
    old_span = 0
    for match in matches:
        span1, span2 = match.span()
        result += content[old_span:span1]
        result += get_template_type(content[span1+2:span2-2])
        old_span = span2
    result += content[old_span:]
    return result