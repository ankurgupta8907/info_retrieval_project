#! /usr/bin/python
# -*- coding: utf-8 -*-

import re as _re
from htmlentitydefs import name2codepoint as _name2codepoint
from urllib import unquote as _unquote


# regular expressions
_body_re=_re.compile("<body[^>]*>(.*)</body>", _re.DOTALL)
_internal_link=_re.compile(("<a href=\"/wiki/([^\":]+)\"[^>]*>(.*?)</a>"), _re.DOTALL)
_interlanguage_link=_re.compile("<li class=\"interwiki-[a-z][a-z]\"><a href=\"http://([a-z][a-z]).wikipedia.org/wiki/([^\"]+)\"", _re.DOTALL)
_link_re=_re.compile(("<a.*?href=\"([^\"]+)\"[^>]*>(.*?)</a>"), _re.DOTALL)
_table_toc_re=_re.compile("<table id=\"toc\" class=\"toc\">.*?</table>", _re.DOTALL)
_img_re=_re.compile("<img[^>]*/>", _re.DOTALL)
_script_re=_re.compile("<script[^>]*>.*?</script>", _re.DOTALL)
_cite_re=_re.compile("<sup[^>]*cite[^>]*>.*?</sup>", _re.DOTALL)
_sup_re=_re.compile("<sup[^>]*>(.*?)</sup>", _re.DOTALL)
_table_re=_re.compile("<table[^>]*>.*?</table>", _re.DOTALL)
_p_and_hx_re=_re.compile("<p>.*?</p>|<h[1-6]>.*?</h[1-6]>")
_tags_re=_re.compile("<[^>]+>")
_end_line_re=_re.compile(u"[^0-9](\.|!|\?|。)[^a-z]", _re.DOTALL)
_entity_re=_re.compile("&([^;\s]+);", _re.DOTALL)

def _entity_callback(matches):
    id = matches.group(1)
    try:
        return unichr(int(id[1:]))
    except:
        try:
            return unichr(_name2codepoint[id])
        except:
            return id




def textExtraction(wikidocument, lang):
    #extract the body part
    body=_body_re.search(wikidocument).group(1)
    
    #list internal links
    internal_links=[(lang, _unquote(url)) for (url, document_name) in _internal_link.findall(body)]
    
    #list interlanguage links
    interlanguage_links=[(lang_ref, _unquote(url)) for (lang_ref, url) in _interlanguage_link.findall(body)]
    
    
    #replace links
    body=_link_re.sub((lambda match: match.group(2)), body)
    
    #supress table toc
    body=_table_toc_re.sub("\n", body)
    
    #supress imgages
    body=_img_re.sub("", body)
    
    #supress scripts
    body=_script_re.sub("", body)
    
    #supress citations
    body=_cite_re.sub("", body)
    
    
    #supress sups
    body=_sup_re.sub((lambda match: match.group(1)), body)
            
    #supress tables
    body=_table_re.sub("\n", body)
            
    ##supress everything after "see also"
    #see_also_re=_re.compile("<h2><span class=\"mw-headline\" id=\"Voir_aussi\">Voir aussi</span></h2>", _re.DOTALL)
    #match=see_also_re.search(body)
    #if match:
        #body=body[:match.start()]
            
    #only keeps p and hx
    body="\n".join(_p_and_hx_re.findall(body))
    
    #remove (formating) tags
    body=_tags_re.sub("", body)
    
    #the following is coding dependant
    body=body.decode("utf8")
    
    #split lines
    body=_end_line_re.sub((lambda match: match.group(0)+"\n"), body)
    
    #encoding normalization
    body=_entity_re.sub(_entity_callback, body)
    
    
    
    return (body.encode("utf8"), internal_links, interlanguage_links)


    
