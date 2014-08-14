#DJANGO_SETTINGS_MODULE = 'ref'
from checkref.models import AUTHOR, REF

if __name__ == '__main__':
    """ Initialize the database """

    bibfile = open('/homes/janeway/zhuww/work/python/django/ref/checkref/myrefs.bib', 'r').read()
    #bibfile = open('short.bib', 'r').read()
    bibitem = bibfile.split('\n@')

    newbib = []

    for item in bibitem:
        item = item[1:] 
        while item[-1] == '\n':
            item = item[:-1]
        newbib.append(item)



    keyset = set(['type'])

    #item = newbib[0]
    allref = []
    for item in newbib:

        record = {}

        n = item.find('{')

        Type = item[:n]
        record.update({'type': Type})
        text = item[n+1:-1]
        n = text.find(',')
        key = text[:n]
        record.update({'id': key})
        content = text[n+1:]

        items = content.split('=')
        n = items[0].rstrip(' ').replace('\n',' ').rfind(' ')
        for i in range(1,len(items)-1):
            key = items[i-1][n:].replace('\n',' ').strip(' "')
            n = items[i].rstrip(' ').replace('\n',' ').rfind(' ')
            value = items[i][:n].strip('" ,\n{}')
            record.update({key:value})
            if not key in keyset:
                keyset.add(key)
        i+=1
        key = items[i-1][n:].replace('\n',' ').strip(' "')
        value = items[i].replace('\n',' ').strip('" ,\n{}')
        record.update({key:value})
        if not key in keyset:
            keyset.add(key)
        allref.append(record)

        Refs = [REF(**x) for x in allref]

        def _dressName(name):
            n = name.find(',')
            last_name = name[:n-1].strip(' {}\n\t')
            if last_name.startswith('\\'):
                last_name = '{'+last_name
            first_name = name[n+1:].strip(' {}')
            return last_name+', '+first_name


        allauthors = []
        allnames = {}
        i = 0
        for ref in Refs:
            authors = ref.author.replace('\n',' ').strip('{}').split(' and ')
            for a in authors:
                aname = _dressName(a.strip(' '))
                if allnames.has_key(aname):
                    author = allauthors[allnames[aname]]
                else:
                    author = AUTHOR(name = aname)
                    author.save()
                    i+=1
                    allnames.update({aname:i})
                    allauthors.append(author)
                ref.author_list.add(author)
            ref.save()

