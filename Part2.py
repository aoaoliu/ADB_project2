import urllib
import json
import re

from Interface import *


class Part2:
    KEY = api_key = open(".api_key").read().strip()

    def __init__(self):
        self.rawQuery = ""
        self.bussinessQuery = ""
        self.bussinessJSON = None
        self.authorQuery = ""
        self.authorJSON = None
        self.results = []
        return

    def run(self, userQuery):
        self.rawQuery = ""
        self.bussinessQuery = ""
        self.bussinessJSON = None
        self.authorQuery = ""
        self.authorJSON = None
        self.results = []

        if self.getQuery(userQuery) is -1:
            return
        self.genMQL()
        self.queryMQL()
        self.parseJSON(self.bussinessJSON, "/organization/organization_founder/organizations_founded")
        self.parseJSON(self.authorJSON, "/book/author/works_written")
        self.sortResults()
        self.output()
        return

    def getQuery(self, userQuery):
        self.rawQuery = userQuery
        self.rawQuery = self.rawQuery.lower()
        if re.match(ur"who created .+\?$", self.rawQuery) is None:
            print("Input format error ! Query must start with 'Who created' and end with '?'")
            return -1

    def genMQL(self):
        realQuery = self.rawQuery[12:self.rawQuery.__len__() - 1]

        bussinessQuery = '[{' +\
                                '"/organization/organization_founder/organizations_founded":' +\
                                    '[{' +\
                                        '"name": null,' +\
                                        '"name~=": "' + realQuery + '"' +\
                                    '}],' +\
                                '"name": null,' +\
                                '"type": "/organization/organization_founder"' +\
                         '}]'
        self.bussinessQuery = bussinessQuery

        authorQuery = '[{' +\
                            '"/book/author/works_written":' +\
                                '[{' +\
                                    '"name": null,' +\
                                    '"name~=": "' + realQuery + '"' +\
                                '}],' +\
                            '"name": null,' +\
                            '"type": "/book/author"' +\
                      '}]'
        self.authorQuery = authorQuery
        return

    def queryMQL(self):
        self.bussinessJSON = self.queryAPI(self.bussinessQuery)
        self.authorJSON = self.queryAPI(self.authorQuery)
        return

    def queryAPI(self, query):
        api_key = self.KEY
        service_url = 'https://www.googleapis.com/freebase/v1/mqlread'
        params = {
                'query': query,
                'key': api_key
        }
        url = service_url + '?' + urllib.urlencode(params)
        response = json.loads(urllib.urlopen(url).read())
        return response

    def parseJSON(self, json, typeName):
        results = json['result']
        # print("\n%s\n" % results)
        for eachResult in results:  # [Name -- [Org1, Org2, Org3,..., OrgN]]
            relation = CreationRelationship()
            relation.creator = eachResult['name']
            if 'author' in typeName:
                relation.authorOrBussiness = "(As Author)"
            elif 'founder' in typeName:
                relation.authorOrBussiness = "(As Bussinessperson)"

            for eachWork in eachResult[typeName]:
                relation.created.append(eachWork['name'])
                # print(eachWork['name'])
            self.results.append(relation)
        return

    def sortResults(self):
        self.results = sorted(self.results, key=lambda result: result.creator)
        # for eachresult in self.results:
            # print eachresult.creator
        return

    def output(self):
        count = 0
        for eachResult in self.results:
            count += 1
            print("%d. " % count),
            print("%s %s created" % (eachResult.creator.encode('utf-8'), eachResult.authorOrBussiness)),
            for i in range(0, eachResult.created.__len__()):
                if i == 0:
                    print("<%s>" % (eachResult.created[i].encode('utf-8'))),
                elif i == eachResult.created.__len__() - 1:
                    print("and <%s>" % (eachResult.created[i].encode('utf-8'))),
                else:
                    print(", <%s>" % (eachResult.created[i].encode('utf-8'))),
            print("")
        print("\n\n\n")
        return
