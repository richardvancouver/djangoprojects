from django.db import models

# Create your models here.

from database.datamodel import keyset#, author, Reference 

#class checkref(models.Model):

class AUTHOR(models.Model):
    name = models.CharField(max_length=20, primary_key=True)
    #last_name = models.CharField(max_length=20)
    #first_name = models.CharField(max_length=20)
    #publiscations = models.ManyToManyField(REF)

    #def __init__(self, name):
        #n = name.find(',')
        #last_name = name[:n-1].strip(' {}\n\t')
        #if last_name.startswith('\\'):
            #last_name = '{'+last_name
        #first_name = name[n+1:].strip(' {}')
        #name = last_name+', '+first_name
        #models.Model.__init__(self,name)


    def __unicode__(self):
        return self.name

class REF(models.Model):
    key = models.CharField(max_length=10, primary_key=True)
    type = models.CharField(max_length=20)
    author = models.CharField(max_length=200)
    journal = models.CharField(max_length=300)
    year = models.IntegerField(null=True)
    doi = models.CharField(max_length=100)
    adsurl = models.CharField(max_length=150)
    adsnote = models.CharField(max_length=150)

    etc = models.CharField(max_length=500)

    author_list = models.ManyToManyField(AUTHOR)

    #for item in keyset-set(['author','journal','year']):
        #locals().update({item: models.CharField(max_length=100)})

    #def __init__(self, **dict):
        #models.Model.__init__(self,**dict)
        #authors = self.author.replace('\n',' ').strip('{}').split(' and ')
        #for a in authors:
            #self.author_list.add(author(a.strip(' ')))

    def __unicode__(self):

        def str2dict(str):
            dic = {}
            str = str.strip('{} \n\t')
            pairs = str.split("',")
            for pair in pairs:
                if not pair.find("':") == -1:
                    pair = pair.split("':")
                    key = pair[0].strip(" u\'\"")
                    value = pair[1].strip(" '\'\"")
                    dic.update({key:value})
            return dic
        
        if self.author.replace('\n',' ').strip('{} ').find(',') == -1:
            Num_of_authors = 0
            etc = str2dict(self.etc)
            if etc.has_key('booktitle'):
                return "%s (%s)" % (etc['booktitle'], self.year)
            elif etc.has_key('title'):
                return "%s (%s)" % (etc['title'], self.year)
            else:
                #return "%s %s" % (self.type, self.year)
                return "%s %s" % (etc, self.year)

        def _dressName(name):
            n = name.find(',')
            last_name = name[:n-1].strip(' {}\n\t')
            if last_name.startswith('\\'):
                last_name = '{'+last_name
            first_name = name[n+1:].strip(' {}')
            return last_name+', '+first_name

        authors = []
        ats = self.author.replace('\n',' ').strip('{}').split(' and ')
        for a in ats:
            authors.append(AUTHOR(name = _dressName(a.strip(' '))))
        Num_of_authors = len(authors)
        if Num_of_authors == 3:
            return "%s, %s and %s  %s" % tuple(authors[:3]+[self.year])
        elif Num_of_authors == 2:
            return "%s and %s  %s" % tuple(authors[:2] + [self.year])
        elif Num_of_authors == 1:
            return "%s %s " %  tuple(authors[:1] + [self.year])
        else:
            return "%s et al. %s " %  tuple(authors[:1] + [self.year])


