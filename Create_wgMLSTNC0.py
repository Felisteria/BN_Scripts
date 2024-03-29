import bns

from wgMLST_Client.wgMLSTSchema import Schema
from wgMLST_Client.wgMLSTSchema import GetCurrentSchema
ExperimentTypes = bns.Database.Db.ExperimentTypes

def loadChr(entry,Exper):
	chrSet = bns.Characters.CharSet()
	if bns.Database.Experiment(entry.Key,Exper).ExperID:
		vals = []
		present = [] 
		chrSet.Load(entry.Key,Exper)
		chrSet.GetData(vals,present)
		return vals,present
	else:
		return None

def ChrCopy(entry,selectedSourceExperiment,selectedDestExperiment,CTExper):
			
	chrSourceSet = bns.Characters.CharSet()
	chrDestSet = bns.Characters.CharSet()
	chrCTSet =  bns.Characters.CharSet()
	if bns.Database.Experiment(entry.Key, selectedSourceExperiment).ExperID:
		vals,present = loadChr(entry,selectedSourceExperiment)
		CTvals,CTpresent = loadChr(entry,CTExper)
		if not bns.Database.Experiment(entry.Key, selectedDestExperiment).ExperID:
			chrDestSet.Create(selectedDestExperiment, "", entry.Key)
		else:
			chrDestSet.Load(entry.Key, selectedDestExperiment)

		for i in range(0,len(vals)):
			if present[i] == 0:
				if CTvals[i] > 0.0:
					present[i]=1
		chrDestSet.SetData(vals,present)
		chrDestSet.Save()


		
def create_copy_wgMLST(wgMLST, copy):
	# create a character type experiment
	chrExperType = ExperimentTypes[copy]
	wgMLSTExperType = ExperimentTypes[wgMLST]
	
	if chrExperType is None:
		chrExperType = ExperimentTypes.Create(copy, 'CHR')
	
	# copy settings
	
	chrExperType.Settings = wgMLSTExperType.Settings

	# create the characters
	copySetType = bns.Characters.CharSetType(copy)
	wgMLSTSetType = bns.Characters.CharSetType(wgMLST)
	for i in range(1, wgMLSTSetType.GetCount()):
		name = wgMLSTSetType.GetChar(i)
		idx = copySetType.AddChar(name, 100.0)
	copySetType.Save()
	


#copy wgMLST, for empty values in wgMLST, look up the value in the call types. If this is 0, fill in 0 in the copy. leave other empty values empty

wgMLST = Schema.GetCurrent().WgMLSTExperTypeName
wgMLST_CT = Schema.GetCurrent().WgMLSTCallTypeExperTypeName

wgMLST_abs0= wgMLST + "_NC0"

if ExperimentTypes[wgMLST_abs0] is None:
	create_copy_wgMLST(wgMLST, wgMLST_abs0)


for entry in bns.Database.Db.Selection:
	ChrCopy(entry,wgMLST,wgMLST_abs0,wgMLST_CT)

	 

		
		


