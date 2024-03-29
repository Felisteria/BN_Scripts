#Script written by Katleen Vranckx for personal use, use of this script is at your own risk

import bns
import datetime
from collections import defaultdict as defaultdict

#Adapt following information to your own database

tags = ["ID"] # tags in fasta header blast hit for which the information needs to be transferred to an entry field, add additional tags seperated by a , and in double quotes
fields = ["ID_AM"] # fields in the database to contain the info in the tags, define in the same order as the tags, add additional fields seperated by a , and in double quotes
BlastDbname = "accepted" # name of the blast database to be used for the blast analysis
exp = "denovo" # name of experiment type to use for the blast analysis
identity_threshold = 65 #Only if the first hit has an identity above the threshold, the results of this hit are parsed
coverage_threshold = 60 #Only if the alignment length/query length of the first hit is higher than the threshold, teh results of the hit are parsed 
CommentField = "Comments_blast" #Name of field to contain comments on the blast results
IDField = "Identity_AM" #Name of the field to store the identity with the hit
LenField = "length_blasthit" #Name of field to store the length of the first blast hit
RunnerUp_threshold = 10 #Minimum difference between first hit and runner up
RunnerUpField = "RunnerUp" #Field to store the ID of a runner up hit

#Do not modify beyond this line, unless you know what you are doing


#setting up the blast calculation
class BlastCalculation(object):
	def __init__(self, BlastDbName,key,exp):
		self.BlastDbName = BlastDbName
		now = datetime.date.today()
		self.blastname = key + "_" + exp + "_" + str(now)
		self.blastwinSave=bns.Blast.BlastWin()
		self.blastjobSave=bns.Blast.BlastJob()
		self.key = key
		self.exp = exp


	def doCalc(self,dct):
		self.blastjobSave.Create(self.blastname)
		self.blastjobSave.SetDatabase(self.BlastDbName,"local")
		self.blastjobSave.SetProgram('blastn')
		self.blastjobSave.AddEntry(self.key,self.exp)
		commObj = dct["communication"]
		self.blastjobSave.SetCalcCommunication(commObj)
		self.blastjobSave.Run()
	
		
	def refresh(self,dct):
		#uncomment to show the window, save needs to be done manually
		#bns.Blast.BlastWin.AttachJob(self.blastwinSave,self.blastjobSave)
		print ("test")

wnd = bns.Windows.BnsWindow(1) 

#creates a dict from a string in the format key sep2 value sep1 key sep2 value sep1...
def createDict(string,sep1,sep2):
	dictfromstring = defaultdict(str)
	pairs = []
	if sep1 in string:
		pairs = string.split(sep1)
	else: #fasta with only one field, so without pipes will result in a list with 1 item
		pairs.append(string)
	for pair in pairs:
		if sep2 in pair:
			key = pair.split(sep2)[0]
			value = pair.split(sep2)[1]
			dictfromstring[key]=value
		else:		
			return None
	return dictfromstring
				
def GetSequence(key, exp):
	"Get the content of a sequence experiment. Returns None if not present"
	if exp  not in bns.Database.Db.ExperimentTypes:
		bns.Util.Warnings.Add("The experiment '{0}' is not present.".format(exp))
	if bns.Database.Experiment(key, exp).ExperID:
		d = {'seq': ""}
		seq = bns.Sequences.Sequence()
		seq.Load(key, exp)
		seq.Get(byref=d)
		return d['seq']				
 
def parse_blasthit(blastjob,tags,nrhit):
	HitParam = {} #dict to contain all parameters on the blast hit
	
	HitParam["ID"] = blastjob.GetHitHSeqKey(nrhit)
	HitParam["Identity"] = blastjob.GetHitIdentity(nrhit)
	HitParam["Len"] = blastjob.GetHitAlignLen(nrhit)
	 #attempt to parse the tags from the header of the hit, if this fails, just return a dict with the tags as key and complete header as value
	HitData = createDict(HitParam["ID"],"|","=") 
	if HitData is None:
		HitData = {} 
		for tag in tags:
			HitData[tag] = blastjob.GetHitHSeqKey(nrhit)
	HitParam["parsed"] = HitData
	return HitParam
	
	

for field in fields:
	currentFields = bns.Database.Db.Fields
	if not field in currentFields:
		currentFields.Add(field)
if not CommentField in currentFields:
	currentFields.Add(CommentField)
	
sel = bns.Database.Db.Selection
for entry in sel:
	if bns.Database.Experiment(entry.Key, exp).ExperID:
		
		
		try: 
			entry.Field(CommentField).Content = "ok"
			obj = BlastCalculation(BlastDbname,entry.Key,exp)
			wnd.StartAsyncCalculation(obj.doCalc, obj.refresh, asynch=False)
			FirstHitParam = parse_blasthit(obj.blastjobSave,tags,0)

			FirstHitCoverage = (FirstHitParam["Len"]/len(GetSequence(entry.Key,exp)))*100
			
			if FirstHitParam["Identity"] < identity_threshold:
				entry.Field(CommentField).Content = "No hit above the identity threshold"
				#continue
				if FirstHitCoverage < coverage_threshold:
					entry.Field(CommentField).Content = "No hit above the coverage threshold"
			else: #only check for runner up if the first hit is above the threshold
				SecondHitParam = parse_blasthit(obj.blastjobSave,tags,1)
				if FirstHitParam["Identity"] - SecondHitParam["Identity"] < RunnerUp_threshold:
					IsRunnerUp = True
				else:
					IsRunnerUp = False
					
					#continue
			for i,tag in enumerate(tags):
				if tag in FirstHitParam["parsed"]:
					entry.Field(fields[i]).Content = FirstHitParam["parsed"][tag]
					#entry.Field(CommentField).Content = "Blast ok"

			if IsRunnerUp:
				entry.Field(RunnerUpField).Content = str(SecondHitParam["parsed"][tags[0]])
			entry.Field(IDField).Content = str(FirstHitParam["Identity"])
			entry.Field(LenField).Content = str(FirstHitParam["Len"])		
		
		except:
			entry.Field(CommentField).Content = "No results"
	bns.Database.Db.Fields.Save()
	

bns.Database.Db.Fields.Save()
