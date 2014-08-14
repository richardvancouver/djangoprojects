# Create your views here.
from django.http import HttpResponse
from django.template import loader, Context
from django.contrib.flatpages.models import FlatPage
from django.shortcuts import render_to_response


from database.datamodel import author, Reference, metadata, author_table, ref_table, author_R_article, keyset
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select

#engine = create_engine('sqlite:///homes/janeway/zhuww/work/python/django/refdb/checkref/ref.db', echo=False)
engine = create_engine('sqlite:///checkref/ref.db', echo=False)

#conn = engine.connect()

def plainRef(ref):
    class plain(object):
        def __init__(self, ref):
            for key in keyset:
                self.__dict__[key] = str(ref.__dict__[key]).strip('{}')
    return plain(ref)


def checkref(request):
    query = request.GET.get('q', '')
    metadata.bind = engine
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    authors = session.query(author).filter_by(last_name=query).all()
    results = []
    for a in authors:
        results += [plainRef(article)  for article in a.articles]
    session.close()
    #return render_to_response(""" """ % results)
    return render_to_response('checkref/checkref.html', {'query': query, 'results': results })
