# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, Context
from django.contrib.flatpages.models import FlatPage
from django.shortcuts import render_to_response
from checkref.models import AUTHOR, REF

from django.core.context_processors import csrf

def populate(file):
    #bibfile = open('/homes/janeway/zhuww/work/python/django/ref/checkref/myrefs.bib', 'r').read()
    #bibfile = open('short.bib', 'r').read()
    bibfile = file.read()
    bibitem = bibfile.split('\n@')

    newbib = []

    for item in bibitem:
        item = item[0:] 
        while item[-1] == '\n':
            item = item[:-1]
        newbib.append(item)



    keyset = set(['type'])

    #item = newbib[0]
    allref = []
    for item in newbib:

        record = {}
        etc = {}

        n = item.find('{')

        Type = item[:n]
        record.update({'type': Type})
        text = item[n+1:-1]
        n = text.find(',')
        key = text[:n].lower()
        record.update({'key': key})
        content = text[n+1:]
        i = content.find('adsurl')
        F0, F1, F2 = False, False, False
        if not i == -1:
            F0 = True
            n = content.find('db_key=')
            if not n  == -1:
                F1 = True
                content = content.replace('db_key=','db_key%')
            m = content.find('bibcode=')
            if not m  == -1:
                F2 = True
                content = content.replace('bibcode=','bibcode%')

        items = content.split('=')
        n = items[0].rstrip(' ').replace('\n',' ').rfind(' ')
        for i in range(1,len(items)-1):
            key = items[i-1][n:].replace('\n',' ').strip(' "\t')
            key = key.lower()
            n = items[i].rstrip(' ').replace('\n',' ').rfind(' ')
            value = items[i][:n].strip('" ,\n\t{}')
            if key in set(['type','key','author','journal','year','doi','adsurl','adsnote']):
                record.update({key:value})
            else:
                etc.update({key:value})
            
            #if not key in keyset:
                #keyset.add(key)
                #REF.objects.raw("alter table checkref_ref add column %s varchar (100)" % (key))
        i+=1
        key = items[i-1][n:].replace('\n',' ').strip(' "\t')
        key = key.lower()
        value = items[i].replace('\n',' ').strip('" ,\n\t{}')
        if F0 and key == 'adsurl':
            if F1:
                value = value.replace('db_key%','db_key=')
            if F2:
                value = value.replace('bibcode%','bibcode=')
        if key in set(['type','key','author','journal','year','doi','adsurl','adsnote']):
            record.update({key:value})
        else:
            etc.update({key:value})
        if not key in keyset:
            keyset.add(key)
        record.update({'etc':etc})
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
            ref.save()
            authors = ref.author.replace('\n',' ').strip('{}').split(' and ')
            for a in authors:
                aname = _dressName(a.strip(' '))
                if allnames.has_key(aname):
                    author = allauthors[allnames[aname]]
                else:
                    author = AUTHOR(name = aname)
                    author.save()
                    allnames.update({aname:i})
                    allauthors.append(author)
                    i+=1
                ref.author_list.add(author)
            ref.save()

    return None
    #return render_to_response('may be may be not',)
    #results = ['May be done, may be not.']
    #return render_to_response('checkref/init.html', {'query': query, 'results': results })


from django import forms

class UploadFileForm(forms.Form):
    #title = forms.CharField(max_length=50)
    file = forms.FileField()

def importfile(request):
    """ Initialize the database """
    if not request.method == 'POST':
        form = UploadFileForm()
        input = {'form': form}
        input.update(csrf(request))
        return render_to_response('checkref/import.html', input)
    else:
        #populate(request.FILES['file'])
        #return render_to_response('checkref/success.html')

        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            populate(request.FILES['file'])
            return render_to_response('checkref/success.html')
        else:
            return render_to_response('checkref/failed.html')


def search(request):
    query = request.GET.get('q', '')
    results = []
    if query:
        results = REF.objects.filter(key__icontains=query)
        if len(results) == 0:
            results = REF.objects.filter(author__icontains=query)
    return render_to_response('checkref/search.html', {'query': query, 'results': results })





