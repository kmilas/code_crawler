from bs4 import BeautifulSoup
from googlesearch import search 
import urllib3
import sys
import os
import random
import re
import Algorithmia
import subprocess

class bcolors:
	HEADER = '\033[95m'
	BLUE = '\033[94m'
	CYAN = '\033[96m'
	YELLOW = '\033[33m'
	RED = '\033[31m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

available_sites = ["w3schools", "stackoverflow", "tutorialspoint", "geeksforgeeks", "pypi",
	"askubuntu"]

programming_keywords_yellow = \
[
	"auto", "long", "enum", "register", "typedef", "extern", "union", "char", 
	"float", "short", "unsigned", "const", "signed", "void", "goto", "sizeof", 
	"bool",	"do", "int", "struct", "_Packed", "double",	"boolean", "byte", 
	"catch", "class", "extends", "instanceof", "interface", "native", 
	"private", "super", "this", "throws", "def", "len",	"lambda", "exit"
]

programming_keywords_cyan = \
[
	"break", "if", "else", "pass", "try", "except", "for", "import", "and", "not", "or",
	"del", "in", "is", "elif", "yield", "with", "from", "print", "raise", "global", 
	"continue", "finally", "while", "assert", "return", "+", "-", "/", "^", "*", "=",
	"<", ">", "/", "|", "&", "@", "%", "&", "*", "~", "exec", "switch", "case", "volatile",
	"default", "static", "abstract", "final", "implements", "new", "package", "protected",
	"public", "strictfp", "synchronized", "throw", "transient", "#include", "True", "true",
	"False", "false"
]

programming_keywords_blue = \
[
	"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"
]

try:
	query = sys.argv[1]
except:
	print("Give search query as argument")
	sys.exit()

rows, columns = os.popen('stty size', 'r').read().split()

http = urllib3.PoolManager()
print()

total_results = []
for url in search(query, tld="com", lang='en', num=10, stop=10, pause=random.uniform(0, 1)): 
	site = [x for x in available_sites if url.find(x)!=-1]
	if(len(site)!=0):
		site = site[0]
	else:
		continue

	if(site in available_sites):
		response = http.request('GET', url)
		soup = BeautifulSoup(response.data, features="lxml")

		try:
			if(site == "w3schools"):
				result = soup.find("div", {"class": "w3-code"})
				result = result.get_text(separator="\n").strip()
			elif(site == "stackoverflow"):
				result = soup.find("div", {"class": "accepted-answer"})
				result = result.find("div", {"class": "s-prose"})
				result = result.find("pre").find(text=True)
			elif(site == "tutorialspoint"):
				result = soup.find("div", {"class": "tutorial-content"})
				result = result.find("pre").find(text=True)	
			elif(site == "geeksforgeeks"):
				result = soup.find("td", {"class": "code"})
				result = result.get_text().strip()
			elif(site == "pypi"):
				result = soup.find("span", id="pip-command")
				result = result.text
			elif(site == "askubuntu"):
				result = soup.find("div", {"class": "accepted-answer"})
				result = result.find("div", {"class": "s-prose"})
				result = result.find("pre").find(text=True)
		except:
			continue

		if result not in total_results:
			total_results.append(result)
		else:
			continue

		print(bcolors.BLUE + site + ": " + bcolors.RED + url + bcolors.ENDC) 
		for i in range(int(columns)):
			print(u'\u2500', end="")

		result = result.strip()

		client = Algorithmia.client('simPbzpOSX4A7ZK6Y4oQjeSGpZ61')
		algo = client.algo('PetiteProgrammer/ProgrammingLanguageIdentification/0.1.3')
		code_lang = algo.pipe(result).result[0]

		print(bcolors.BLUE + "This code is in: " + code_lang[0] 
			+ "\nProbability: " + str(code_lang[1]) + "\n" + bcolors.ENDC)

		process = subprocess.Popen(["pygmentize", "-f", "terminal"],
			stdin=subprocess.PIPE, stdout=subprocess.PIPE)
		process.stdin.write(result.encode())
		print(process.communicate()[0].decode())
		process.stdin.close()