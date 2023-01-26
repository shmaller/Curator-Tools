'''
Content Metadata Tag Parser 2.0.2
Nicholas Boni
Staff Content Curator
January 26, 2023
'''

def parse_tag_data(datafile):
	'''
	Inputs: tab-delimited txt file of content metadata tags,
	with headers organized as follows:
	DOCID, TAG1, TAG2, TAG3, TAG4, TAG5, TAGGENERIC

	Outputs: list of tag dictionaries. Each dictionary contains 
	all data for one tag. Each key is a tag, and each value is
	a list of all docids which have that tag.
	'''

	# docid, stripe, tag1, tag2, tag3, tag4, tag5, tag_gen
	list_of_tag_dicts = [{},{},{},{},{},{},{},{}]

	with open(datafile) as f:
		for line in f:
			row = line.strip('\n').split('\t')

			docid = row[0]

			for i in range(1,8):
				tag = row[i]

				if tag == '':
					pass
				elif tag in list_of_tag_dicts[i]:
					list_of_tag_dicts[i][tag].append(docid)
				elif tag not in list_of_tag_dicts[i]:
					list_of_tag_dicts[i][tag] = [docid]
				else:
					print('Unexpected error loading tag into dictionary.')
					print(tag,list_of_tag_dicts[i])
					return

	return list_of_tag_dicts

################################################################

def parse_grouping_data(groupings_file):
	'''
	Inputs: txt file of tag grouping data (copy/pasted
	Column B from the groupings Excel sheet. Each page
	is delimited by a '*'. Currently needs to be manually
	updated when new tags are added.)

	Outputs: Dictionary where grouping_s names are keys,
	values are lists of all tags in that grouping.
	'''
	
	groupings_dict = {}
	list_of_pages = []
	list_of_groupings = []
	
	with open(groupings_file) as f:
		workbook_data = f.read()
		list_of_pages = workbook_data.split('*') # each page of the Excel workbook is delimited by a '*'

		for page in list_of_pages:
			list_of_groupings.append(page.strip().split('\n'))

		for grouping in list_of_groupings:
			for tag in grouping:
				if '_s' in tag:
					_s_grouping = tag
					if _s_grouping not in groupings_dict:
						groupings_dict[_s_grouping] = []
				else:
					groupings_dict[_s_grouping].append(tag)

	return groupings_dict

################################################################

def generate_searchmetadata_query(list_of_tag_dicts,groupings_dict):
	'''
	Inputs: List of tag dictionaries generated by
	parse_tag_data(datafile).

	Outputs: string of SearchMetadata query for each tag.
	
	Takes the tag data from parse_tag_data, and compiles it
	into a string containing the appropriate Search Metadata
	query syntax.
	'''

	set_of_all_docids = set()

	HEADER = "SEARCH METADATA TAGS\nSee the readme file for instructions.\n\nCONFIGURATION\
	\nHits: 5000\nFields: id,title,stripe_s,grouping1_s,grouping2_s,grouping3_s,grouping4_s,grouping5_s,tagsgeneric_s\n\n"
	QUERY_BASE = "and(or(and(nicontenttype:or(knowledgebase,tutorial,supplemental,compatibility),uri:en-us),and(nicontenttype:example,nilanguage:en)),documentid:or("
	outstr = HEADER

	for tag_dict in list_of_tag_dicts:
		for tag in tag_dict:

			outstr += 'TAG: %s\n'%tag

			for grouping in groupings_dict:
				if tag in groupings_dict[grouping]:
					outstr += 'GROUPING: %s\n\n'%grouping
					break

			outstr += QUERY_BASE

			for docid in tag_dict[tag]:
				outstr += docid + ','
				set_of_all_docids.add(docid)

			# delete final comma - causes syntax error
			# in Search Metadata
			outstr = outstr[:len(outstr)-1]

			outstr += '))\n\n'

	outstr += 'ALL DOC IDS TAGGED\n\n'
	outstr += QUERY_BASE
	for docid in set_of_all_docids:
		outstr += docid + ','
	outstr = outstr[:len(outstr)-1]
	outstr += '))'

	return outstr

################################################################


def write_searchmetadata_query_to_file(query):
	'''
	Inputs: string of SearchMetadata query syntax
	as generated by generate_searchmetadata_query(list_of_tag_dicts).

	Outputs: None.

	Writes query to a txt file called "query.txt" in same directory
	as program.
	'''

	with open('output.txt','w') as f:
		f.write(query)
	
################################################################

def main():
	'''
	Inputs: None.

	Outputs: None.

	1. Parses tag data from file into list of tag dictionaries.
	2. Generates SearchMetadata query syntax from list of tag dictionaries.
	3. Writes SearchMetadata query to file.
	'''

	import os.path

	if not os.path.isfile('groupings.txt'):
		input('"groupings.txt" not found. Make sure "groupings.txt"' \
		' is in the same directory as this program and try again.')
		quit()

	infile = input('Enter the name of your tag data text file: ')

	if not os.path.isfile(infile):
		response = input('Invalid filename or file not found. Try again or type "quit" to quit. ')
		if response == "quit":
			quit()
		else:
			main()

	list_of_tag_dicts = parse_tag_data(infile)
	groupings_dict = parse_grouping_data('groupings.txt')
	query = generate_searchmetadata_query(list_of_tag_dicts,groupings_dict)
	write_searchmetadata_query_to_file(query)

	input('Operation complete! Check the directory of this program for "output.txt". Press Enter to quit.')

################################################################

if __name__ == '__main__':
	main()