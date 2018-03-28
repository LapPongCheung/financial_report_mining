import re

def page_break(file):
	f = open(file, 'r', encoding = 'utf-8')
	lines = f.readlines()

	breaks = []

	for num, line in enumerate(lines):
		if '\f' in line:
			breaks.append(num)

	return breaks

def divide_into_sections(file):
	f = open(file, 'r', encoding = 'utf-8')
	lines = f.readlines()

	breaks = []

	for num, line in enumerate(lines):
		if '\f' in line:
			breaks.append(num)
	#remove special line "JOBNAME"
	new_breaks = []
	for i in range(len(breaks)):
		if r'JOBNAME' in lines[breaks[i]]:
			new_breaks.append(breaks[i] + 2)
		else:
			new_breaks.append(breaks[i])
	breaks = new_breaks

	sections = {}
	title = ''
	previous_title = ''
	current_section = []
	for i in range(len(breaks)):
		title = lines[breaks[i]]
		if title != previous_title and i != 1:
			sections[previous_title] = current_section
			current_section = []
		try:
			content = lines[breaks[i]:breaks[i+1]]
		except:
			content = lines[breaks[i]:-1]
			current_section.extend(content)
			sections[title] = current_section
			break
		current_section.extend(content)
		previous_title = title

	return sections



if __name__ == "__main__":
	link = r'./testing_data/06080'
	breaks = divide_into_sections(link)
