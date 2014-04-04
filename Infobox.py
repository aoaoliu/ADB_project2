#!/usr/bin/python
import json
import urllib
import re


"""
This is a nice observation that we expected you to have while implementing this system and interacting with freebase and the reference implementation.
 
The reference implementation decides to group the "people-related" entities in case a person exhibits multiple entity types. However, the League-Person (BusinessPerson, Author, Actor), League-Team, and Team-Person (Buesinessperson, Author, Actor) merges are not allowed, and this is a design choice for what make sense in what we model :). Keep in mind that even Google and Bing give different infoboxes for the same query,
 
So, what is the correct answer in such cases and what is expected from you? I would encourage you to follow the reference implementation. However, all combinations are allowed and no points will be deducted. What is required, of course, is to group the people-related entities. The rest of the design (the 3 merges-or not- above) is up to you. Moreover, note that we require just one infobox. Which means that you should not output one for the NFL as League and one for NFL as Author. Finally, you are required to reason on your design choices in your README.
 
Best,
   -Fotis
"""
"""
What is definitely in the grading criteria is what you the infobox displays (properties and their extracted values.)
"""


#api_key = open(".api_key").read().strip()
api_key = "AIzaSyAdpaZqPgCVg9q1_KIeL8Y--LSLZ1UaJD4"
freebase_entity_types = {
	'/type/object': 'Basic',
	'/people/person': 'Person',
	'/common/topic': 'Basic',
	'/people/deceased_person': 'Person',
	'/book/author': 'Author',
	'/book/book_subject': 'Author',
	'/influence/influence_node': 'Author',
	'/film/actor': 'Actor',
	'/tv/tv_actor': 'Actor',
	'/organization/organization_founder': 'BusinessPerson',
	'/business/board_member': 'BusinessPerson',
	'/sports/sports_league': 'League',
	'/organization/organization': 'League',
	'/sports/sports_team': 'SportsTeam',
	'/sports/professional_sports_team': 'SportsTeam'
}
ENTITY_TYPE = re.compile(r'^/\w+/\w+')
freebase_mapping = {
	##### Person #####
	'/type/object/name': 'Name',
	'/people/person/date_of_birth': 'Birthday',
	'/people/person/place_of_birth': 'Place of birth', # 'Place of Birth'
	#'': 'Death(Place, Date, Cause)',
	'/people/deceased_person/place_of_death': 'Death(Place)',
	'/people/deceased_person/date_of_death': 'Death(Date)',
	'/people/deceased_person/cause_of_death': 'Death(Cause)',
	'/people/deceased_person/death': 'Death',
	'/people/person/sibling_s': 'Siblings',
	'/people/person/spouse_s': 'Spouses',
	'/common/topic/description': 'Descriptions', # 'Description'

	##### Author #####
	'/book/author/works_written': 'Books', # 'Books(Title)'
	'/book/book_subject/works': 'Books about', # 'Book About the Author(Title)'
	'/influence/influence_node/influenced': 'Influenced',
	'/influence/influence_node/influenced_by': 'Influenced By', # 'Influenced by'

	##### Actor #####
	'/film/actor/film': 'Films', # 'FilmsParticipated(Film, Name, Character)'

	##### BusinessPerson #####
	'/business/board_member/leader_of': 'Leadership', # 'Leadership(From, To, Organization, Role, Title)'
	'/business/board_member/organization_board_memberships': 'Board Member', # 'BoardMember(From, To, Organization, Role, Title)'
	'/organization/organization_founder/organizations_founded': 'Founded', # 'Founded(OrganizationName)'

	##### League #####
	#'': 'Name', # we have obtained this by '/type/object/name'
	'/sports/sports_league/championship': 'Championship',
	'/sports/sports_league/sport': 'Sport',
	'/organization/organization/slogan': 'Slogan',
	'/common/topic/official_website': 'OfficialWebsite',
	#'': 'Description', # we have obtained this by '/common/topic/description'
	'/sports/sports_league/teams': 'Teams',

	##### SportsTeam #####
	#'': 'Name', # we have obtained this by '/type/object/name'
	#'': 'Description', # we have obtained this by '/common/topic/description'
	'/sports/sports_team/sport': 'Sport',
	'/sports/sports_team/arena_stadium': 'Arena',
	'/sports/sports_team/championships': 'Championships',
	'/sports/sports_team/coaches': 'Coaches', # 'Coaches(Name, Position, From, To)'
	'/sports/sports_team/founded': 'Founded',
	'/sports/sports_team/league': 'Leagues',
	'/sports/sports_team/location': 'Locations',
	'/sports/sports_team/roster': 'PlayersRoster' # 'PlayersRoster(Name, Position, Number, From, To)'
}


def print_headline(name, list):
	upline = (" " * 9) + ("-" * 99)
	print upline
	if len(list) == 0:
		temp = name
	else:
		temp = name + ' (' + (', '.join(list)) + ')'
	N = (50 - int(len(temp)/2))
	print (' ' * 8) + '|',
	print (' ' * N) + temp + (' ' * (100 - N - len(temp) - 2)) + '|'
	print upline
	return


def print_description(content):
	# we only print the first description
	#content = content[0].encode("utf8", "ignore")
	content = content[0]
	temp = ''
	for i in range(len(content)):
		if content[i] == '\n':
			temp += ' '
		else:
			temp += content[i]
	content = temp

	upline = (' ' * 9) + ('-' * 99)
	print (' ' * 8) + '| '  + 'Descriptions:' + (' ' * 3),
	while len(content) > 81:
		print content[0:81] + '|'
		content = content[81:]
		print (' ' * 8) + '| ' + (' ' * 16),
	print content[:] + (' ' * (81 - len(content))) + '|'
	print upline
	return


def print_left(s):
	while len(s) > 77:
		print (' ' * 8) + '|' + (' ' *20),
		print s[0:77] + ' ' + '|'
		s = s[77:]
	print (' ' * 8) + '|' + (' ' *20),
	print s + (' ' * (78 - len(s))) + '|'
	return

def print_list(name, list):
	if len(list) == 0:
		return

	# if there are several items in a list, we add a mark to each of them
	if len(list) > 1:
		for i in range(len(list)):
			list[i] = str(i+1) + ') ' + list[i]

	# print the first item in the list
	upline = (' ' * 9) + ('-' * 99)
	print (' ' * 8) + '| ' + name + ':' + (' ' * (15 - len(name))),
	if len(list[0]) > 80:
		print list[0][0:80] + ' ' + '|'
		print_left(list[0][80:])
	else:
		print list[0] + (' ' * (81 - len(list[0]))) + '|'

	if len(list) == 1:
		print upline
	else:
		for i in range(1,len(list)):
			print (' ' * 8) + '|' + (' ' * 17),
			if len(list[i]) > 80:
				print list[i][0:80] + ' ' + '|'
				print_left(list[i][80:])
			else:
				print list[i] + (' ' * (81 - len(list[i]))) + '|'
		print upline
	return


def print_table(name, table):
	#'Films': [[character, film],[],[],[],...] (all strings; if empty '' will be returned)
	#'Leadership': [[organization, role, title, time],[],[],[],...] (all strings; if sth is empty, '' returned)
	#'Board Member': [[organization, role, title, time],[],[],[],...] (all strings; if sth is empty, '' returned)
	#'Coaches': [[name, position, time],[],[],[],...] (all strings; if sth is empty, '' returned)
	#'PlayersRoster': [[name, position, number, time],[],[],[],...] (all strings; if sth is empty, '' returned)
	upline = (" " * 9) + ("-" * 98)
	if name == 'Films':
		print '        | Films:         ',
		print '|Character                              | Film Name                               |'
		print (' ' * 8) + '|' + (' ' * 16),
		print ('-' * 82)
		for item in table:
			print (' ' * 8) + '|' + (' ' * 16),
			if len(item[0]) > 38:
				item[0] = item[0][0:35] + '...'
			if len(item[1]) > 39:
				item[1] = item[1][0:36] + '...'
			print '|' + item[0] + (' ' * (39 - len(item[0]))) + '| ' + item[1] + (' ' * (40 - len(item[1]))) + '|'
		print upline
	if name == 'Leadership':
		print '        | Leadership:    ',
		print '|Organization            | Role            | Title            | From-To           |'
		print (' ' * 8) + '|' + (' ' * 16),
		print ('-' * 82)
		for item in table:
			print (' ' * 8) + '|' + (' ' * 16),
			if len(item[0]) > 23:
				item[0] = item[0][0:20] + '...'
			if len(item[1]) > 15:
				item[1] = item[1][0:12] + '...'
			if len(item[2]) > 16:
				item[2] = item[2][0:13] + '...'
			if len(item[3]) > 17:
				item[3] = item[3][0:14] + '...'
			print '|' + item[0] + (' ' * (24 - len(item[0]))) + '| ' + item[1] + (' ' * (16 - len(item[1]))) + '| ' + item[2] + (' ' * (17 - len(item[2]))) + '| ' + item[3] + (' ' * (18 - len(item[3]))) + '|'
		print upline
	if name == 'Board Member':
		print '        | Board Member:  ',
		print '|Organization            | Role            | Title            | From-To           |'
		print (' ' * 8) + '|' + (' ' * 16),
		print ('-' * 82)
		for item in table:
			print (' ' * 8) + '|' + (' ' * 16),
			if len(item[0]) > 23:
				item[0] = item[0][0:20] + '...'
			if len(item[1]) > 15:
				item[1] = item[1][0:12] + '...'
			if len(item[2]) > 16:
				item[2] = item[2][0:13] + '...'
			if len(item[3]) > 17:
				item[3] = item[3][0:14] + '...'
			print '|' + item[0] + (' ' * (24 - len(item[0]))) + '| ' + item[1] + (' ' * (16 - len(item[1]))) + '| ' + item[2] + (' ' * (17 - len(item[2]))) + '| ' + item[3] + (' ' * (18 - len(item[3]))) + '|'
		print upline
	if name == 'Coaches':
		print (' ' * 8) + '| Coaches:        |Name                    | Position                    | From/To                  |'
		print (' ' * 8) + '|' + (' ' * 16),
		print ('-' * 82)
		for item in table:
			print (' ' * 8) + '|' + (' ' * 16),
			if len(item[0]) > 23:
				item[0] = item[0][0:20] + '...'
			if len(item[1]) > 27:
				item[1] = item[1][0:24] + '...'
			if len(item[2]) > 24:
				item[2] = item[2][0:21] + '...'
			print '|' + item[0] + (' ' * (24 - len(item[0]))) + '| ' + item[1] + (' ' * (28 - len(item[1]))) + '| ' + item[2] + (' ' * (25 - len(item[2]))) + '|'
		print upline
	if name == 'PlayersRoster':
		print (' ' * 8) + '| PlayersRoster:  |Name             | Position             | Number            | From/To            |'
		print (' ' * 8) + '|' + (' ' * 16),
		print ('-' * 82)
		for item in table:
			print (' ' * 8) + '|' + (' ' * 16),
			if len(item[0]) > 16:
				item[0] = item[0][0:13] + '...'
			if len(item[1]) > 20:
				item[1] = item[1][0:17] + '...'
			if len(item[2]) > 17:
				item[2] = item[2][0:14] + '...'
			if len(item[3]) > 18:
				item[3] = item[3][0:15] + '...'
			print '|' + item[0] + (' ' * (17 - len(item[0]))) + '| ' + item[1] + (' ' * (21 - len(item[1]))) + '| ' + item[2] + (' ' * (18 - len(item[2]))) + '| ' + item[3] + (' ' * (19 - len(item[3]))) + '|'
		print upline
	return


def print_hash(table, type_of_entities):
	#----------------- extract type of entity  of interests here -----------------
	class_list = []
	for category in ['League', 'SportsTeam']:
		if len(type_of_entities[category]) != 0:
			class_list.append(category)
			#for item in type_of_entities[category]:
			#	if len(type_of_entities[category][item]) != 0:
			#		class_list.append(category)
			#		break
	for category in ['Author', 'Actor', 'BusinessPerson']:
		if len(type_of_entities[category]) != 0:
			for item in type_of_entities[category]:
				if len(type_of_entities[category][item]) != 0:
					class_list.append(category)
					break

	if 'SportsTeam' in class_list:
		class_list = ['SportsTeam'] # we only need this information for a team
	if 'League' in class_list:
		class_list = ['League'] # we only need this information for a league
	
	#print "Types:"
	#print  class_list
	print_headline(table['/type/object/name'][0], class_list)

	#------------------ information extraction -----------------------------------
	if 'SportsTeam' in class_list or 'League' in class_list:
		class_list.append('Basic')
	else:
		class_list.append('Basic')
		class_list.append('Person')
	if 'League' not in class_list and len(type_of_entities['Basic']) != 0 and '/common/topic' in type_of_entities['Basic'] and '/common/topic/official_website' in type_of_entities['Basic']['/common/topic']:
		type_of_entities['Basic']['/common/topic'].remove('/common/topic/official_website')
	#----------------------------------------------------------------------------


	#================== formalize the death information ===================
	if '/people/deceased_person/place_of_death' in table or '/people/deceased_person/date_of_death' in table or '/people/deceased_person/cause_of_death' in table:
		try:
			place = table['/people/deceased_person/place_of_death'][0]
			del table['/people/deceased_person/place_of_death']
		except:
			place = ''
		try:
			date = table['/people/deceased_person/date_of_death'][0]
			del table['/people/deceased_person/date_of_death']
		except:
			date = ''
		try:
			cause = table['/people/deceased_person/cause_of_death'][0]
			del table['/people/deceased_person/cause_of_death']
		except:
			cause = ''
		del type_of_entities['Person']['/people/deceased_person'][:]
		type_of_entities['Person']['/people/deceased_person'].append('/people/deceased_person/death')
		if date != '' and place != '' and cause != '':
			death = date + ' at ' + place + ', cause: (' + cause + ')'
		elif date != '' and place != '':
			death = date + ' at ' + place
		elif place != '' and cause != '':
			death = 'at ' + place + ', cause: (' + cause + ')'
		elif date != '' and cause != '':
			death = date + ', cause: (' + cause + ')'
		else:
			if date != '':
				death = date
			elif place != '':
				death = 'at ' + place
			elif cause != '':
				death = 'cause: (' + cause + ')'
			else:
				death = ''
		if death == '':
			del type_of_entities['Person']['/people/deceased_person']
		else:
			table['/people/deceased_person/death'] = [death]
	#print table['/people/deceased_person/death']

	# the order for the six higher categories
	class_temp = ['Basic', 'Person', 'Author', 'BusinessPerson', 'Actor', 'League', 'SportsTeam']
	temp = []
	for i in range(len(class_temp)):
		if class_temp[i] in class_list:
			temp.append(class_temp[i])
	class_list = temp

	for key in class_list:
		for key1 in type_of_entities[key]:
			for key2 in type_of_entities[key][key1]:
				name = freebase_mapping[key2]
				content = table[key2]
				if name == 'Descriptions':
					print_description(content)
				elif name in ['Films', 'Leadership', 'Board Member', 'Coaches', 'PlayersRoster']:
					print_table(name, content)
				else:
					print_list(name, content)
				#for item in table[key2]:
				#	print item
				#print ''
	return


def map(entity):
	if entity in freebase_mapping:
		return True
	else:
		return False


def supported(mid):
	url = 'https://www.googleapis.com/freebase/v1/topic' \
		+ mid + '?' + 'key=' + api_key
	response = json.loads(urllib.urlopen(url).read())
	result = response['property']

	# this demonstrates the mapping relations
	type_of_entities = {
		'Basic': {}, # <name> and <description> for all queries; <officialwebsite> for league only
		'Person': {},
		'Author': {},
		'Actor': {},
		'BusinessPerson': {},
		'League': {},
		'SportsTeam': {}
	}
	type_list = []

	#DEBUG
	#print result
	
	for item in result: # item here is kind of types of freebase; we should map them to those 
				# we have interests in, and extract the values
		result[item] = result[item]['values']
		if item == '/type/object/type': # use this to confirm which entities to extract
			for item1 in result[item]:
				type = item1['id']
				match = ENTITY_TYPE.match(type)
				if match:
					temp = match.group()
					if temp in freebase_entity_types:
						#print temp
						#print freebase_entity_types[temp]
						type_of_entities[freebase_entity_types[temp]][type] = []

	type_of_entities['Basic']['/type/object'] = [] # for name entity specially; each item always has a name

	for item in result: # extract the entity names we need
		match = ENTITY_TYPE.match(item)
		if match:
			temp = match.group()
			if temp in freebase_entity_types: # potential matching item
				if map(item) == True: # we do this map because not all the sub properties do we have interests in
					
					# DEBUG
					#print item
					if temp in type_of_entities[freebase_entity_types[temp]]:
						type_of_entities[freebase_entity_types[temp]][temp].append(item)
						type_list.append(item)
	#print ''
	# DEBUG
	#print "This is the entity directory:"
	#print type_of_entities
	#print ''
	#print "This are all the entities we need to extract:"
	#print type_list
	#print ''

	result_extracted = {}
	# In this project, you should only worry about the text, value, id, and property properties 
	# in order to extract the values for the parent property
	for item in result:
		if item in type_list:
			result_extracted[item] = result[item]
	# DEBUG
	#print "This is the ecxtracted results(waiting to be processed to get detailed information):"
	#print result_extracted

	return (result_extracted, type_of_entities, type_list)


def result_concat(table, url): # e.g. cause_of_death: Cardiac arrest, Homicide
	try:
		temp = []
		for pos in table[url]['values']:
			try:
				temp.append(pos['text'])
			except:	
				continue
		result = ', '.join(temp)
	except:
		result = ''
	return result


def result_list(table, url):
	result= []
	for item1 in table[url]:
		try:
			result.append(item1['text'])
		except:
			continue
	return result


def getentity(result_extracted, type_of_entities, type_list):
	result = {}
	for item in type_list:
		result[item] = []

		##### Person #####
		if item in ['/type/object/name', '/people/person/date_of_birth', '/people/person/place_of_birth', '/people/deceased_person/place_of_death', '/people/deceased_person/date_of_death']:
			result[item] = result_list(result_extracted, item)
		if item == '/people/deceased_person/cause_of_death':
			result[item] = result_list(result_extracted, item)
			result[item] = [', '.join(result[item])]
		if item == '/people/person/sibling_s':
			for item1 in result_extracted[item]: # each item1 here is a sibling
				property = item1['property']
				sibling = result_concat(property, '/people/sibling_relationship/sibling')
				result[item].append(sibling)
		if item == '/people/person/spouse_s':
		# return format: [[spouse, time, location],[],[],[],...] (all strings; if something is empty, '' is returned)
			for item1 in result_extracted[item]: # each item1 here is a spouse
				property = item1['property']
				spouse = result_concat(property, '/people/marriage/spouse')
				begin = result_concat(property, '/people/marriage/from')
				end  = result_concat(property, '/people/marriage/to')
				location = result_concat(property, '/people/marriage/location_of_ceremony')
				# let each of the elements be a printable spouse
				# spouse + ' (' + begin + ' - ' + end + ') @ ' + location
				if begin == '':
					time = begin
				elif end == '':
					time = '(' + begin + ' - now)'
				else:
					time = '(' + begin + ' - ' + end + ')'
				if time == '' and location == '':
					temp = spouse
				elif time == '':
					temp = spouse + ' @ ' + location
				else:
					temp = spouse + ' ' + time
				result[item].append(temp)
		if item == '/common/topic/description':
			for item1 in result_extracted[item]: # each item1 is a description
				result[item].append(item1['value'])

		##### Author #####
		if item in ['/book/author/works_written', '/book/book_subject/works', '/influence/influence_node/influenced', '/influence/influence_node/influenced_by']:
			result[item] = result_list(result_extracted, item)

		##### Actor #####
		# not use: "/tv/tv_actor"
		if item == '/film/actor/film':
		# return format: [[character, film],[],[],[],...] (all strings; if empty '' will be returned)
			for item1 in result_extracted[item]: # each item1 here is a film with actor
				property = item1['property']
				character = result_concat(property, '/film/performance/character')
				film = result_concat(property, '/film/performance/film')
				result[item].append([character, film])

		##### BusinessPerson #####
		if item == '/business/board_member/leader_of':
		# return format: [[organization, role, title, time],[],[],[],...] (all strings; if sth is empty, '' returned)
			for item1 in result_extracted[item]: # each item1 here is a leadership
				property = item1['property']
				organization = result_concat(property, '/organization/leadership/organization')
				role = result_concat(property, '/organization/leadership/role')
				title = result_concat(property, '/organization/leadership/title')
				begin = result_concat(property, '/organization/leadership/from')
				end = result_concat(property, '/organization/leadership/to')
				if begin == '':
					time = begin
				elif end == '':
					time = '(' + begin + ' / now)'
				else:
					time = '(' + begin + ' / ' + end + ')'
				result[item].append([organization, role, title, time])
		if item == '/business/board_member/organization_board_memberships':
		# return format: [[organization, role, title, time],[],[],[],...] (all strings; if sth is empty, '' returned)
			for item1 in result_extracted[item]: # each item1 here is a boardmembership
				property = item1['property'] # we should extract each item in property
				organization = result_concat(property, '/organization/organization_board_membership/organization')
				role = result_concat(property, '/organization/organization_board_membership/role')
				title = result_concat(property, '/organization/organization_board_membership/title')
				begin = result_concat(property, '/organization/organization_board_membership/from')
				end = result_concat(property, '/organization/organization_board_membership/to')
				if begin == '':
					time = begin
				elif end == '':
					time = '(' + begin + ' / now)'
				else:
					time = '(' + begin + ' / ' + end + ')'
				result[item].append([organization, role, title, time])
		if item == '/organization/organization_founder/organizations_founded':
		# return format: [string1, string2, string3, ...]
			result[item] = result_list(result_extracted, item)

		##### League #####
		if item in ['/sports/sports_league/championship', '/sports/sports_league/sport', '/organization/organization/slogan', '/common/topic/official_website']:
			result[item] = result_list(result_extracted, item)
		if item == '/sports/sports_league/teams':
		# return format: [string1, string2, string3, ...]
			for item1 in result_extracted[item]:
				property = item1['property']

				team = result_concat(property, '/sports/sports_league_participation/team')
				result[item].append(team)

		##### SportsTeam #####
		if item in ['/sports/sports_team/sport', '/sports/sports_team/arena_stadium', '/sports/sports_team/championships', '/sports/sports_team/founded', '/sports/sports_team/location']:
			result[item] = result_list(result_extracted, item)
		if item == '/sports/sports_team/coaches':
		# return format: [[name, position, from, to],[],[],[],...] (all strings; if sth is empty, '' returned)
			for item1 in result_extracted[item]: # each item1 here is a boardmembership
				property = item1['property'] # we should extract each item in property
				name = result_concat(property, '/sports/sports_team_coach_tenure/coach')
				position = result_concat(property, '/sports/sports_team_coach_tenure/position')
				begin = result_concat(property, '/sports/sports_team_coach_tenure/from')
				end = result_concat(property, '/sports/sports_team_coach_tenure/to')
				if begin == '':
					time = begin
				elif end == '':
					time = begin + ' / now'
				else:
					time = begin + ' / ' + end
				result[item].append([name, position, time])
		if item == '/sports/sports_team/league':
		# return format: [string1, string2, string3, ...]
			for item1 in result_extracted[item]: # each item1 here is a league
				property = item1['property'] # we should extract each item in property
				league = result_concat(property, '/sports/sports_league_participation/league')
				result[item].append(league)
		if item == '/sports/sports_team/roster':
		# return format: [[name, position, number, time],[],[],[],...] (all strings; if sth is empty, '' returned)
			for item1 in result_extracted[item]: # each item1 here is a roster
				property = item1['property'] # we should extract each item in property
				name = result_concat(property, '/sports/sports_team_roster/player')
				position = result_concat(property, '/sports/sports_team_roster/position')
				number = result_concat(property, '/sports/sports_team_roster/number')
				begin = result_concat(property, '/sports/sports_team_roster/from')
				end = result_concat(property, '/sports/sports_team_roster/to')
				if begin == '':
					time = begin
				elif end == '':
					time = begin + ' / now'
				else:
					time = begin + ' / ' + end
				result[item].append([name, position, number, time])
	return result


def check_six(type_list, type_of_entities, result_extracted):
	#print type_of_entities
	#print result_extracted['/type/object/name'][0]['text']
	#DEBUG
	#print type_list
	"""
	for url in type_list:
		match = ENTITY_TYPE.match(url)
		type = match.group()
		if freebase_entity_types[type] in ['Person', 'Author', 'Actor', 'BusinessPerson', 'League', 'SportsTeam']:
			return True
	"""
	# For the '/tv/tv_actor', we use it to judge whether this 'mid' is what we need (has at least one of the six higher-level entities), but we don't use its sub-entities to extract effective information. So there is possibly a scenario in which we have "xxx (Actor)", but the following infobox only have 'Name' and 'Description' entities, but not something about the 'Actor'.
	#for entity in ['Person', 'Author', 'Actor', 'BusinessPerson', 'League', 'SportsTeam']:
	#	if len(type_of_entities[entity]) != 0:
	#		return True
	if len(type_of_entities['SportsTeam']) == 0:
		pass
	else:
		return True
		"""
		for item in type_of_entities['SportsTeam']:
			if len(type_of_entities['SportsTeam'][item]) != 0:
				return True
		"""

	if len(type_of_entities['League']) == 0:
		pass
	else:
		for item in type_of_entities['League']:
			if item == '/organization/organization':
				continue
			else:
				return True

	if len(type_of_entities['Person']) == 0:
		pass
	else:
		return True

	return False



#if __name__ == '__main__':
def infobox(query):

	# optional
	#print("Please input query:")
	#query = raw_input()

	#print "Processing.. Please wait..."
	#query = 'NY Knicks'
	#query = 'Jackson'
	#query = 'NBA'

	#query = "Itsik Pe'er"
	#query = "bill gates"
	service_url = 'https://www.googleapis.com/freebase/v1/search'
	params = {
		'query': query,
		'key': api_key
	}
	url = service_url + '?' + urllib.urlencode(params)
	response = json.loads(urllib.urlopen(url).read())
	result = response['result']
	mid = []
	for item in result:
		mid.append(item['mid'])
	#print mid
	#print len(mid)

	i = 0
	NO_RESULT = True
	for i in range(len(mid)):
		(result_extracted, type_of_entities, type_list) = supported(mid[i])
		#if len(type_list) == 0:
		if not check_six(type_list,  type_of_entities, result_extracted):
			if (i+1)%5 == 0:
				print "%s Search API result entries were considered. None of them of a supported type."%(i+1)
			continue
		else:
			NO_RESULT = False
			break
	
	# DEBUG
	#print type_list
	#print type_of_entities

	if NO_RESULT:
		#print "No results for query \"%s\"." %(query)
		print "No related information about query [%s] was found!" % query
	else:
		entity = getentity(result_extracted, type_of_entities, type_list)
		# for entity, key is the freebase entity name, and value is the values for that entity, which is a string list
		print_hash(entity, type_of_entities)
