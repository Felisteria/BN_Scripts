import bns

from wgMLST_Client import AlleleCalls
from wgMLST_Client.wgMLSTSchema import Schema
from wgMLST_Client.create_sampledb import CreateExperType

from collections import defaultdict

def CreateChars(inExperType, outExperType, comm):
	comm.SetMessage("Creating characters for experiment '{}' ...".format(outExperType.DispName))
	
	inCst = bns.Characters.CharSetType(inExperType.Name)
	inChars = [inCst.GetChar(i) for i in xrange(inCst.GetCount())]
	
	outCst = bns.Characters.CharSetType(outExperType.Name)
	outChars = { outCst.GetChar(i): i for i in xrange(outCst.GetCount())}
	
	outCst.NoSave()
	index = { inChar: outChars[inChar] if inChar in outChars else outCst.AddChar(inChar, 5000) for inChar in inChars }
	outCst.Save()
	
	return index	
	

def Export(entry, inExperType, settings, comm):
	attach = bns.Database.ExperAttachments(entry.Key, inExperType.Name)
	
	#content = attach['AlleleFinderResult_']
	#afLocusCalls = AlleleCalls.LocusCalls.CallsFromString(content)
		
	
	for key, s in settings.iteritems():
		if s['attachmentId'] not in attach.keys(): continue
		
		
		content = attach[s['attachmentId']]
		calls = AlleleCalls.LocusCalls.CallsFromString(content)
		index = s['index']
		
		vals = [0]*len(index)
		presences = [0]*len(index)
		
		for locus, locusCalls in calls.iteritems():
			if len(locusCalls.calls)!=1: continue
			#if locus in afLocusCalls and len(afLocusCalls[locus].calls)!=1: continue
			
			for call in locusCalls.calls:
				
				#if locus=='LMO_2517':
				#	i=0
				try:
					if float(call.alleleId)>0 and call.Similarity==100.0:
						vals[index[locus]] = float(call.alleleId)
						presences[index[locus]] = 1
				except:
					pass
				
		cs = bns.Database.Experiment(entry, s['experType']).LoadOrCreate()
		cs.SetData(vals, presences)
		cs.Save()
		
		
	
def DoExport(winId):
	
	entries = list(bns.Database.Db.Selection)
	currSchema = Schema.GetCurrent()

	wgmlstExperType = bns.Database.ExperimentType(currSchema.WgMLSTExperTypeID)

	#make sure the experiment types exist
	wgmlstExperTypeName_AF = CreateExperType(wgmlstExperType.Name + '_AF', wgmlstExperType.DispName+'_AF', 'CHR', [], [], currSchema.WgMLSTExperTypeSettings)	
	wgmlstExperTypeName_AB = CreateExperType(wgmlstExperType.Name + '_AB', wgmlstExperType.DispName+'_AB', 'CHR', [], [], currSchema.WgMLSTExperTypeSettings)

	def DoCalc(args):
		comm = args.get('communication', bns.Windows.CalcCommunication())
		
		settings = {}
		wgmlstExperType_AB = bns.Database.Db.ExperimentTypes[wgmlstExperTypeName_AB]
		index = CreateChars(wgmlstExperType, wgmlstExperType_AB, comm)
		settings['Assembly-based calls'] = {
			'experType':  wgmlstExperType_AB,
			'attachmentId': '_BLASTAlleleFinderResult_',
			'index' : index
		}
		
		wgmlstExperType_AF = bns.Database.Db.ExperimentTypes[wgmlstExperTypeName_AF]
		index = CreateChars(wgmlstExperType, wgmlstExperType_AF, comm)
		settings['Assembly-free calls'] = {
			'experType':  wgmlstExperType_AF,
			'attachmentId': 'AlleleFinderResult_',
			'index': index
		}
		
		for i, e in enumerate(entries):
			comm.SetMessage("Extracting locus calls for entry {} ...".format(e.DispName))
			Export(e, wgmlstExperType, settings, comm)
			comm.SetProgress(i+1, len(entries)) 
			if not comm.MustContinue(): return
		
		
	def DoRefresh(args):
		pass
		
	bns.Windows.BnsWindow(winId).StartAsyncCalculation(DoCalc, DoRefresh, False)


	
#if __bnsdebug__ and __name__ == '__main__':
DoExport(1)
