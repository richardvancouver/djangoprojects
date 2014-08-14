from django.db import models

# Create your models here.

from database.datamodel import keyset#, author, Reference 

#class checkref(models.Model):

class AUTHOR(models.Model):
    name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    first_name = models.CharField(max_length=20)
    #publiscations = models.ManyToManyField(REF)
    def __init__(self, name):
        n = name.find(',')
        self.last_name = name[:n-1].strip(' {}\n\t')
        if self.last_name.startswith('\\'):
            self.last_name = '{'+self.last_name
        self.first_name = name[n+1:].strip(' {}')
        self.name = self.last_name+', '+self.first_name


    def __unicode__(self):
        return self.name

class REF(models.Model):
    key = models.CharField(max_length=10)
    for key in keyset:
        if key in set(['year','month','volumn','pages']):
            locals().update({key: models.IntegerField()})
        else:
            locals().update({key: models.CharField(max_length=100)})
    author_list = models.ManyToManyField(AUTHOR)

    def __init__(self, **dict):
        models.Model.__init__(**dict)
        #self.__dict__.update(dict)
        #for key in keyset:
            #if not self.__dict__.has_key(key):
                #self.__dict__.update({key:''})
        authors = self.author.replace('\n',' ').strip('{}').split(' and ')
        for a in authors:
            #aut = author(a.strip(' '))
            #ext = exists().where(author.name == aut.name)
            #if ext:
                #print 'Repeat!!!!!!:', aut
                #self.author_list.append(author_table.execute(ext))
            #else:
                #self.author_list.append(aut)
            self.author_list.add(author(a.strip(' ')))

    def __unicode__(self):
        authors = self.author.replace('\n',' ').strip('{}').split(' and ')
        for a in authors:
            self.author_list.append(author(a.strip(' ')))
        Num_of_authors = len(self.author_list)
        if Num_of_authors == 3:
            return "%s, %s and %s  %s" % tuple(self.author_list[:3]+[self.year])
        elif Num_of_authors == 2:
            return "%s and %s  %s" % tuple(self.author_list[:2] + [self.year])
        elif Num_of_authors == 1:
            return "%s %s " %  tuple(self.author_list[:1] + [self.year])
        else:
            return "%s et al. %s " %  tuple(self.author_list[:1] + [self.year])


if __name__ == '__main__':
    """ Initialize the database """

    bibfile = open('myrefs.bib', 'r').read()
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

        Refs = [Reference(**x) for x in allref]

        allauthors = []
        allnames = set()
        for ref in Refs:
            for author in ref.author_list:
                if author.name in allnames:
                    pass
                else:
                    allnames.add(author.name)
                    allauthors.append(author)
                    author.save()
                #author.publiscations.add(ref)
            ref.save()

