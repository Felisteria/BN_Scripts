#//$menu window=main;popup=WGS tools;insertafter=Synchronize;name=Redo submission of new alleles for selected entries...

import bns
from wgMLST_Client import AlleleCalls
from wgMLST_Client import ClientSettings
from wgMLST_Client.wgMLSTSchema import Schema
import xml.etree.cElementTree as ET
from Bio.Seq import Seq
from collections import defaultdict


MessageBox = bns.Util.Program.MessageBox

def Reevaluate(locusCalls):
	errorDict = {'success':True,'error':""}
	
	def AllowCalc():

		hasScriptFunc = hasattr(bns.Windows.BnsWindow(1), 'IsCalculationBusy')
		if hasScriptFunc:
			return not bns.Windows.BnsWindow(1).IsCalculationBusy()
		else:
			return True
			
	def startAsync():
		"""Submits selected new alleles
		"""
		if AllowCalc:
			
			bns.Windows.BnsWindow(1).StartAsyncCalculation(_Reevaluate,_Refresh, False)
			

	def _Reevaluate(dct):
	
		calcComm = dct['communication']

		calcComm.SetMessage('Checking alleles to be submitted')
		submitSettings = ClientSettings.WgMLSTClientSettings.GetCurrent()
		
		annseq = bns.Sequences.AnnSeq()
		
		try:
			annseq.Create(locusCalls.entry.Key, Schema.GetCurrent().DeNovoExperTypeName)
		except:
			errorDict['error']="de novo sequence could not be loaded"
			errorDict['success']=False
			return
		
		

		try:
			result = locusCalls.attachmentContents['_BLASTAlleleFinderResult_']
			
		except:

			errorDict['error']="no experiment attachment with blast results"
			errorDict['success']=False
			return
		
		locusIds = locusCalls.CallsFromString(result)
		locusIdsToSubmit = defaultdict(list)
		
		#load whole sequence and split in contigs as start and stop of alleles is stored as the position on the contig
		seq = annseq.GetSeq(0, annseq.GetLen())		
		contigs= seq.split('|')
		
		for call,locus in locusIds.items():
			i=0
			for allele in locus.calls:
				if allele.IsNew:
					if not allele.qualities['si'] == 100.0:
						contig = str(allele.Contig)
						contigID = int(contig.strip('denovo_'))

						if allele.Orientation == 1:
#							print contigs[contigID][allele.Start:allele.Stop]
							alleleSeq = contigs[contigID][allele.Start:allele.Stop] #annseq is 0-based
						else:
							alleleSeq = Seq(contigs[contigID][allele.Start:allele.Stop]).reverse_complement()
							
#						print alleleSeq
						allele.sequences['s'] = alleleSeq
#						print allele.CanSubmit()
#						print allele.CanAutoSubmit(submitSettings)
						if	 allele.CanSubmit() and allele.CanAutoSubmit(submitSettings):
							locusIdsToSubmit[call].append(allele)
							
					elif not allele.CanAutoSubmit(submitSettings):
						locusIds[call].calls[i].qualities['si']=85.0
						locusIds[call].calls[i].alleleId = 1
				i+=1
							
		locusCalls.attachmentContents['_BLASTAlleleFinderResult_'] = locusCalls.CallsToString(locusIds)		
		print(locusCalls.attachmentContents['_ConsensusResult_'])
		if len(locusIdsToSubmit)>0:	
			calcComm.SetMessage('Submitting {0} alleles for entry {1}'.format(len(locusIdsToSubmit),locusCalls.entry))
			try:
				locusCalls.SubmitNewAlleles('_BLASTAlleleFinderResult_', locusIdsToSubmit,calcComm)
			except:
				errorDict['error']="resubmission failed for unknown reason, please try again later"
				errorDict['success']=False
				return
				
			
			if not calcComm.MustContinue():
				raise RuntimeError("Script has been stopped by user.")
		return
			
	

	def _Refresh(dct):
			
		
		locusCalls.InterSectCalls()	

	#bns.Windows.BnsWindow(1).StartAsyncCalculation(_Reevaluate,_Refresh,async=False)
	
	startAsync()
	return errorDict['success'],errorDict['error']

		
if __name__=='__main__':
	from wgMLST_Client.wgMLSTSchema import GetCurrentSchema

	errorList= "Key\tError"
	successCount = 0
	if not bns.Database.Db.Selection:
		MessageBox("Error", "No entries selected.", "exclamation")
	for entry in bns.Database.Db.Selection:
		if bns.Database.Experiment(entry, Schema.GetCurrent().WgMLSTExperTypeName).IsPresent():
			
			locusCalls = AlleleCalls.LocusCalls("", entry, Schema.GetCurrent().WgMLSTExperTypeName)
		#	print locusCalls.attachmentContents['_BLASTAlleleFinderResult_']
		#	print locusCalls.attachmentContents['_NewAllelesOnHold_']
			success,error = Reevaluate(locusCalls)
			if not success:
				errorList= errorList + "\n{0}\t{1}".format(entry.Key,error)
			else:
				successCount= successCount+1
	if len(errorList) > 10:
		bns.Util.IO.ExportAndView(errorList)
	
	MessageBox("Success", "{0} entries succesfully re-evaluated".format(successCount), "exclamation")
				
