import os, sys, time, re, random, math, math
import requests
from bs4 import BeautifulSoup

def GetPage(url): 
	return requests.get(url).text
def GetFile(fn): 
	with open(fn, encoding='utf-8') as fin: return fin.read()

def EditDist(xx, yy):
	f = [[max(x, y) for y in range(1+len(yy))] for x in range(1+len(xx))]
	for i in range(1, len(xx)+1):
		for j in range(1, len(yy)+1):
			if xx[i-1] == yy[j-1]: f[i][j] = f[i-1][j-1]
			else: f[i][j] = min(f[i][j-1], f[i-1][j], f[i-1][j-1]) + 1
	return f[-1][-1]
			
class ListExtractor:
	def __init__(self, page, selector='', verbose=True, minlen=4):
		self.treepos = {}
		self.treesr = []
		self.soup = BeautifulSoup(page, 'html.parser')
		if selector != '':
			self.results = [self.GetResultWithSelector(selector)]
		else:
			print('Analyzing...')
			self.Scan(minlen)
		if verbose:
			self.ShowResults()

	def MakeNodeStr(self, nindex):
		pos = len(self.treesr)
		node = self.nodes[nindex]
		self.treesr.append(node.name)
		for ch in self.childinds[nindex]:
			self.MakeNodeStr(ch)
		self.treesr.append('/'+node.name)
		pos = (pos, len(self.treesr))
		self.treepos[nindex] = pos

	def GetTreeStr(self, node):
		return self.treesr[self.treepos[node][0]:self.treepos[node][1]]

	def Similar(self, nindex, sindex):
		node = self.nodes[nindex]
		sib = self.nodes[sindex]
		if node.name != sib.name: return False
		nodec = node.attrs.get('class', [])
		sibc = sib.attrs.get('class', [])
		if 'active' in nodec: nodec.remove('active')
		if 'active' in sibc: sibc.remove('active')
		if len(nodec) > 0:
			comm = [x for x in nodec if x in set(sibc)]
			clsdist = 1 - len(comm) / max(len(nodec),len(sibc))
		else: clsdist = 1
		ntree = self.GetTreeStr(nindex)
		stree = self.GetTreeStr(sindex)
		treedist = EditDist(ntree, stree)
		treedist = treedist / min(len(ntree), len(stree))
		if treedist * clsdist < 0.3: return True
		return False

	def Scan(self, minlen=4):
		soup = self.soup
		nodes = [soup.body]; qh = 0
		parinds = [-1]; childinds = [[]]
		while qh < len(nodes):
			z, zi = nodes[qh], qh; qh += 1
			for ch in z.children:
				if type(ch) is not type(z): continue
				if ch.name in ['script', 'style', 'noscript']: continue
				childinds[zi].append(len(nodes))
				parinds.append(zi)
				childinds.append([])
				nodes.append(ch)
		self.nodes = nodes
		self.childinds = childinds
		self.MakeNodeStr(0)
		score = {}; sprev = {}
		for nindex, node in enumerate(nodes):
			pindex = parinds[nindex]
			psibinds = list(reversed([i for i in range(pindex+1,nindex) if parinds[i] == pindex]))
			#spsibs = list(node.find_previous_siblings())
			#for sindex in psibinds: assert nodes[sindex] in spsibs
			for sindex in psibinds:
				sim = self.Similar(nindex, sindex)
				if sim: 
					score[nindex] = score.get(sindex, 0) + 1
					sprev[nindex] = sindex
					if not sindex in score: score[sindex] = 0
					break
		self.score = score
		results = [];  used = set()
		for nindex, node in enumerate(nodes):
			if nindex in used: continue
			ulist = []; mxn = -1  
			for ind in reversed(childinds[nindex]):
				if not ind in score: continue
				if mxn < 0 or score[ind] > score[mxn]: mxn = ind
			while mxn >= 0:
				used.add(mxn)
				ulist.append(nodes[mxn])
				mxn = sprev.get(mxn, -1)
			ulist.reverse()
			if len(ulist) > 0: results.append(ulist)
		used = set(); newret = []
		for ulist in results:
			text = ' '.join([re.sub('\s', '', x.text) for x in ulist])
			if text in used: continue
			if len(ulist) < minlen: continue
			used.add(text)
			newret.append(ulist)
		self.results = newret
		self.SortResults()

	def SortResults(self):
		def sortfunc(ulist):
			sm = 0
			for node in ulist:
				text = re.sub('\s', '', node.text)
				sm += math.sqrt(len(text))
			return sm
		self.results.sort(key=sortfunc, reverse=True)
		
	def ShowResults(self, reverse=True):	
		rlist = reversed(list(enumerate(self.results))) if reverse else enumerate(self.results)
		for index, ulist in rlist:
			node = ulist[0]; par = node.parent
			p_header = str(par).split('>')[0]+'>'
			print('List %d: %d items' % (index, len(ulist)))
			print(p_header)
			for ii, node in enumerate(ulist):
				header = str(node).split('>')[0]+'>'
				text = node.text.strip()
				text = text.replace('\r', '')
				text = text.replace('\t', ' ')
				text = re.sub('[\n]+', ' ', text)
				text = re.sub('[ ]+', ' ', text)
				print(' '*4+header)
				print(' '*8+text)
			print('-' * 30)
		print('Total %d lists' % len(self.results))

	def MakeSelector(self, num=0, verbose=False):
		ulist = self.results[num]
		par = ulist[0].parent
		iname = ulist[0].name
		icls = set(ulist[0].attrs.get('class', []))
		for node in ulist:
			cls = set(node.attrs.get('class', []))
			icls.intersection_update(cls)
		fea2 = iname+''.join('.'+x for x in icls)
		testlist = par.select(fea2)
		if verbose: print(fea2)
		if len(testlist) != len(ulist) or testlist[-1] != ulist[-1]: return ''
		pname = par.name
		pcls = par.attrs.get('class', [])
		pid = par.attrs.get('id', '')
		fea1 = pname
		if len(pid) != 0: fea1 += '#'+pid
		else: fea1 += ''.join('.'+x for x in pcls)
		testps = self.soup.select(fea1)
		if verbose: print(fea1)
		if len(testps) == 0 or testps[0] != par: return ''
		return ' '.join([fea1, fea2])		

	def GetResultWithSelector(self, selector):
		return self.soup.select(selector)
		
	def GetResult(self, num=0):
		return self.results[num]


if __name__ == '__main__':
	url = 'https://search.jd.com/Search?keyword=7600k&enc=utf-8&wq=7600k&pvid=fa96fc1671a64649ac9784ab2872c871'
	url = 'http://pwnable.kr/play.php'
	#page = GetPage(url)
	page = GetFile('1.txt')
	ex = ListExtractor(page)
	print(ex.MakeSelector())
	print('completed')
