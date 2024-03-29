#//$menu window=main;popup=WGS tools;insertafter=Synchronize;name=Calculate additional quality statistics for selected entries...

# this script will calculate some additional quality parameters and store it in the quality experiment type. It uses the settings for the WGS tools plugin, so it can be run without adapting the script in any database with the plugin.
# the additional stats are 'CorePercent'; 'NrCoreAlleles'; 'NrCoreMultiAlleles';'GC%_raw';'GC%_trimmed'
# the first time this script is run in a database, these additional characters are created in the quality experiment, any analysis window needs to be closed to allow the addition of these characters. 
import bns
from wgMLST_Client.CommonTools.Settings import StoredSettings

# call type character values encoding for AB multiple calls
multValues = set([10, 11, 16, 17, 18, 19, 20, 21, 22])

Dlg = bns.Windows.XmlDlgBuilder

class SelectAspectDlg(Dlg.Dialogs):
	def __init__(self, expID, expName):
		Dlg.Dialogs.__init__(self, 'SelectAspectDlg')
		
		# the values to show in the list control
		cst = bns.Characters.CharSetType(expID)
		self.aspects = [cst.ViewGet(id) for id in cst.ViewGetList()]
		self.values = [aspect.GetInfo()['DisplayName'] for aspect in self.aspects]
		coreAspect = [value for value in self.values if 'Core' in value or 'core' in value][0]
		
		# the list controls
		self.coreList = Dlg.SimpleList('core', self.values, len(self.values)+1, 40, multi=False, default=coreAspect)
		
		# now define the dialog layout
		grid = [["Select scheme:", self.coreList]]
		simple = Dlg.SimpleDialog(grid, onStart=self.onStart, onOk=self.onOk)
		self.AddSimpleDialog(expName, simple)
	
	def onStart(self, args):
		"""Set the selected items"""
		pass
	
	def onOk(self, args):
		"""Get the selected items"""
#		self.coreAspect = self.aspects[self.values.index(self.coreList.GetValue())].GetID()
		self.coreAspect = self.coreList.GetValue()
		
def GetAspectLoci(entry, experId, aspectName):
	cst = bns.Characters.CharSetType(experId)	
	aspectIds = cst.ViewGetList()
	for aspectId in aspectIds:
		view = cst.ViewGet(aspectId)
		name = view.GetInfo()['DisplayName']
		if name == aspectName:
			return view.GetCharacters()
	raise RuntimeError("Isolate {0}: invalid aspect {2} for {1}.".format(entry.DispName, bns.Database.ExperimentType(experId).DispName, aspectName))

def CalculateCorePercent(entry, experId, coreAspectName):
	hasAlleleIds = False
	nCore = None
	
	exper = bns.Database.Experiment(entry, experId)
	if exper.IsPresent():
		cst = bns.Characters.CharSetType(experId)
		try:
			coreAspect = GetAspectLoci(entry, experId, coreAspectName)

		except RuntimeError as e:
			raise RuntimeError("Isolate {0}: invalid core aspect {2} for {1}.".format(entry.DispName, bns.Database.ExperimentType(experId).DispName, coreAspectId))
			
		hasAlleleIds = True
		
		coreLocusIdxs = set(cst.FindChar(locus) for locus in coreAspect)
		values = []
		presences = []
		
		chrSet = exper.LoadOrCreate()
		chrSet.GetData(values, presences)
		nPresent = sum(p for i, p in enumerate(presences) if i in coreLocusIdxs)
		nLoci = len(coreLocusIdxs)
	
	corePercent = float(nPresent)/float(nLoci)*100 if hasAlleleIds else '?'
	return corePercent

def SaveCharVal(entry, chrExpName, chrName, chrValue):
	changed = 0
	chrSet = bns.Characters.CharSet()
	if bns.Database.Experiment(entry.Key, chrExpName).ExperID:
		chrSet.Load(entry.Key, chrExpName)
	else:
		chrSet.Create(chrExpName, '', entry.Key)
	idx = chrSet.FindName(chrName)
	if idx<0:
		idx=bns.Characters.CharSetType(chrExpName).AddChar(chrName,100)
	if chrValue == '?':
		chrSet.SetAbsent(idx)
	else:
		chrSet.SetVal(idx, float(chrValue))
		changed = 1
	chrSet.Save()
	return changed
	
def CalculateCoreAlleles(entry, experId, coreAspectName, allAspectName):
	hasAlleleIds = False
	nCore = None
	nAcc = None
	
	exper = bns.Database.Experiment(entry, experId)
	if exper.IsPresent():
		allAspect = GetAspectLoci(entry, experId, allAspectName)
		coreAspect = GetAspectLoci(entry, experId, coreAspectName)
		
		hasAlleleIds = True
		
		cst = bns.Characters.CharSetType(experId)
		locusIdxs = set(cst.FindChar(locus) for locus in allAspect)
		coreLocusIdxs = set(cst.FindChar(locus) for locus in coreAspect)
		values = []
		presences = []
		
		chrSet = exper.LoadOrCreate()
		chrSet.GetData(values, presences)
		nPresent = sum(p for i, p in enumerate(presences) if i in locusIdxs)
		nCore = sum(p for i, p in enumerate(presences) if i in coreLocusIdxs)
		nAcc = nPresent - nCore
	
	return hasAlleleIds, nCore, nAcc

def CalculateMultAlleles(entry, experId, aspectName):
	hasAlleleIds = False
	nMult = None
	
	exper = bns.Database.Experiment(entry, experId)
	if exper.IsPresent():
		aspect = GetAspectLoci(entry, experId, aspectName)
		
		# call types
		experId += '_CallTypes'
		exper = bns.Database.Experiment(entry, experId)
		if exper.IsPresent():
			hasAlleleIds = True
			
			cst = bns.Characters.CharSetType(experId)
			locusIdxs = set(cst.FindChar(locus) for locus in aspect)
			values = []
			presences = []
			
			chrSet = exper.LoadOrCreate()
			chrSet.GetData(values, presences)
			
			# multiple ab call values
			nMult = sum(p for i, (p, d) in enumerate(zip(presences, values)) if (i in locusIdxs) and (d in multValues))
			
	return hasAlleleIds, nMult

def CalculateGC(key, srsName):
	if bns.Database.Experiment(key, srsName).ExperID:
		srs = bns.SequenceReadSets.SeqReadSet()
		srs.Load(key, srsName)
		info = {}
		srs.GetInfo(info)
		gcBaseCount = info['CountG'] + info['CountC']
		allBaseCount = info['CountA'] + info['CountC'] + info['CountG'] + info['CountT'] + info['CountOther']
		PercentGC_wgs = (100.0 * gcBaseCount) / allBaseCount if allBaseCount else 0
		return PercentGC_wgs
	else:
		return None
	

def CheckChar(chrExpName,chrName):
	chrSetType = bns.Characters.CharSetType(chrExpName)
	idx = chrSetType.FindChar(chrName)
	if idx<0:
		idx=chrSetType.AddChar(chrName,100)	
		
def main(corePercentChar, coreAlleleChar, coreMultChar, GC, GC_trimmed):
	changes = 0
	settings = StoredSettings('WGMLST_CLIENT_SCHEMA_SETTINGS',
												'wgMLSTExperTypeName', 'wgMLSTExperTypeID',
												'qualityExperTypeName', 'qualityExperTypeID',
												'wgsExperTypeName','wgsExperTypeID')		
	dlg = SelectAspectDlg(settings.wgMLSTExperTypeID, settings.wgMLSTExperTypeName)
	if not dlg.Show():
		bns.Stop()
	corePercentChar = dlg.coreAspect + "_" + corePercentChar
	coreAlleleChar = dlg.coreAspect + "_" + coreAlleleChar
	coreMultChar = dlg.coreAspect + "_" + coreMultChar
	CheckChar(settings.qualityExperTypeID,corePercentChar)
	CheckChar(settings.qualityExperTypeID,coreAlleleChar)
	CheckChar(settings.qualityExperTypeID,coreMultChar)
	CheckChar(settings.qualityExperTypeID,GC)
	CheckChar(settings.qualityExperTypeID,GC_trimmed)
	
	for i, entry in enumerate(bns.Database.Db.Selection):
		bns.SetBusy("Processing {0} entries...".format(i))
		corePercent = CalculateCorePercent(entry, settings.wgMLSTExperTypeID, dlg.coreAspect)
		changed = SaveCharVal(entry, settings.qualityExperTypeID, corePercentChar, corePercent)
		changes += changed
		hasCore,coreAlleles,accAlleles = CalculateCoreAlleles(entry, settings.wgMLSTExperTypeID, dlg.coreAspect, "wgMLST loci")
		if hasCore:
			SaveCharVal(entry, settings.qualityExperTypeID, coreAlleleChar, coreAlleles)
		hasMult,multCore = CalculateMultAlleles(entry, settings.wgMLSTExperTypeID, dlg.coreAspect)
		if hasMult:
			SaveCharVal(entry, settings.qualityExperTypeID, coreMultChar, multCore)
		PercentGC = CalculateGC(entry.Key,settings.wgsExperTypeName)
		if PercentGC:
			SaveCharVal(entry, settings.qualityExperTypeID, GC, PercentGC)
		PercentGC_trimmed = CalculateGC(entry.Key,settings.wgsExperTypeName+'_TrimmedStats')
		if PercentGC_trimmed:
			SaveCharVal(entry, settings.qualityExperTypeID, GC_trimmed, PercentGC_trimmed)
	bns.SetBusy("")
	bns.Util.Program.MessageBox("Report", "Additional statistics for {0} entries saved.".format(changes), 'information')
	
if __name__ == '__main__':
	corePercentChar = 'PercentCalled'
	coreAlleleChar = 'NrAlleles'
	coreMultChar = 'NrMultiAlleles'
	GC = 'GC%_raw'
	GC_trimmed = 'GC%_trimmed'
	

	
	main(corePercentChar, coreAlleleChar, coreMultChar, GC, GC_trimmed)
