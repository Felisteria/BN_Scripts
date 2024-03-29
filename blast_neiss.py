import bns
import datetime




			
			
now = datetime.datetime.now()
blastwin=bns.Blast.BlastWin()
blastwinSave=bns.Blast.BlastWin()
blastjob=bns.Blast.BlastJob()
blastjobSave=bns.Blast.BlastJob()
blastname = "BlastJob" + str(now)
blastjob.Create("blast")
blastjobSave.Create(blastname)
blastjob.SetDatabase("genomes","local")
blastjob.SetProgram('blastn')
blastjobSave.SetDatabase("genomes","local")
blastjobSave.SetProgram('blastn')
exps = ["adk","fumC","abcZ","aroE","gdh","pdhC","pgm"]

#setting up the blast calculation
class BlastCalculation(object):
	def doCalc(self,dct):
		commObj = dct["communication"]
		blastjobSave.SetCalcCommunication(commObj)
		blastjobSave.Run()
	def refresh(self,dct):
		bns.Blast.BlastWin.AttachJob(blastwinSave,blastjobSave)

wnd = bns.Windows.BnsWindow(1) 
obj = BlastCalculation()
for exp in exps:
	currentFields = bns.Database.Db.Fields
	if not exp+"_Species" in currentFields:
		currentFields.Add(exp+"_Species")
	if not exp+"_Identity" in currentFields:
		currentFields.Add(exp+"_Identity")
sel = bns.Database.Db.Selection
for entry in sel:
	for exp in exps:
		if bns.Database.Experiment(entry.Key, exp).ExperID:
			try: 
				blastjob.Reset()
				blastjob.AddEntry(entry.Key,exp)
				blastjobSave.AddEntry(entry.Key,exp)
				blastjob.Run()
				FirstHit = blastjob.GetHitHSeqKey(0)
				FirstHitData = FirstHit.split("|")
			
				Species = FirstHitData[1]

		
				entry.Field(exp+"_Species").Content = Species
				FirstHitIdentity = blastjob.GetHitIdentity(0)
				entry.Field(exp+"_Identity").Content= str("%.2f" %FirstHitIdentity)
			except:
				print "No results"
	bns.Database.Db.Fields.Save()
	

bns.Database.Db.Fields.Save()
wnd.StartAsyncCalculation(obj.doCalc, obj.refresh, asynch=False)
