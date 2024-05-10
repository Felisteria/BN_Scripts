#Stores the annotation of each CDS in expGenome in a seperate entry in the sequence expGene with the fields of the annoation, except translation, in an entry field
#script written by Katleen Vranckx for own use

import bns
ExperimentTypes = bns.Database.Db.ExperimentTypes
Fields = bns.Database.Db.Fields

#adapt to database:
expGenome= "denovo"
expGene= "gene"
AccField= "SV__VERSION"
DescrField = "OS__SOURCE"
searchterm1 = "pts"
searchterm2 = ""
searchterm3 = ""
#qualDict= {"/organism=":"Strain"}
#qualDict=  {"/locus_tag=" : "gene","/product=":"description","/protein_id=":"accession"}
field = bns.Database.EntryField

def OpenSequence(key, exper):
	"""Load a sequence belonging to a key-experiment pair
	if the sequence does not exist yet, create one
	"""
	seq = bns.Sequences.Sequence()
	if bns.Database.Experiment(key, exper).ExperID:
		seq.Load(key, exper)
	else:
		seq.Create(exper, "", key)
	return seq
	
for entry in bns.Database.Db.Selection:

	"Get the content of a sequence experiment. Returns None if not present"
	if expGenome  not in ExperimentTypes:
		bns.Util.Warnings.Add("The experiment '{0}' is not present.".format(exp))
	if bns.Database.Experiment(entry.Key, expGenome).ExperID:
#		d = {'seq': ""}
		seq = bns.Sequences.AnnSeq()
		seq.Create(entry.Key, expGenome)
		feature = bns.Sequences.AnnFts()
		
		for featureIdx in range(0,seq.GetFtsCnt()):
			seq.GetFts(feature,featureIdx)
			nrQual = feature.GetQlfCnt()
			featurekey = feature.GetKey()
			if featurekey == "CDS":
				for qualID in range(0,nrQual):
					qualKey = feature.GetQlfKey(qualID).strip('/= ') # remove backspace, equal sign and possible trailing leading spaces as this is bad for use in field name
					if "product" in qualKey: # look for the product annotation
						qual = feature.GetQlfData(qualID).lower()
						if searchterm1 in qual and searchterm2 in qual and searchterm3 in qual:
							for qualID2 in range(0,nrQual):
								qualKey2 = feature.GetQlfKey(qualID2).strip('/= ')
								if "protein_id" in qualKey2:
									proteinID = feature.GetQlfData(qualID2)
									
							if not qualKey in Fields: #if a field with the same name as the qualifier does not exist, create it
								Fields.Add(qualKey)	
							if not qualKey2 in Fields: #if a field with the same name as the qualifier does not exist, create it
								Fields.Add(qualKey2)							
							cdsEntry = bns.Database.Db.Entries.Add()
							field(cdsEntry.Key,qualKey).Content = qual
							field(cdsEntry.Key,qualKey2).Content = proteinID
							geneSeqExp = OpenSequence(cdsEntry.Key,expGene) #create or load sequence for each CDS feature with the searchterms to store sequence of CDS
							geneSeq = seq.GetSeq(feature.GetStart()-1,feature.GetEnd()-1)
							geneSeqExp.Set(geneSeq)

							if feature.GetOrientation() > 0:
								geneSeqExp.Invert()
								geneSeqExp.Compl()
							geneSeqExp.Save()
							field(cdsEntry.Key,AccField).Content = field(entry.Key,AccField).Content # copy accession to new entry to keep track of what comes from where
							field(cdsEntry.Key,DescrField).Content = field(entry.Key,DescrField).Content
				
				bns.Database.Db.Fields.Save()
				
					
						
						
#		seq.Get(byref=d)
#		return d['seq']
	
	

#for entry in bns.Database.Db.Entries:
#	seq = GetSequence(entry.Key, "16S rDNA")
#	if seq is not None:
#		print(entry.Key + ':\t' + seq)
#
