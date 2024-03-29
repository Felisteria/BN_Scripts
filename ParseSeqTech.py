#Script that checks complete GenBank header for the presence of the sequencing technology used. Note 454 is not reliable as is cannot be distinguished from presence of 454 in numerical information
#Script written by Katleen Vranckx for own use


import bns

ExperimentTypes = bns.Database.Db.ExperimentTypes
exp= "denovo"
seqTechs = ["IonTorrent","PacBio","Illumina","454"]

field = bns.Database.EntryField

	
for entry in bns.Database.Db.Selection:
	if exp not in ExperimentTypes:
		bns.Util.Warnings.Add("The experiment '{0}' is not present.".format(exp))
	if bns.Database.Experiment(entry.Key, exp).ExperID:

		seq = bns.Sequences.AnnSeq()
		seq.Create(entry.Key, exp)
		header = ""
		seqTechID = False
		for i in range(0,seq.GetHeaderLineCnt()):
			header = header + seq.GetHeaderLineByIndex(i)
		print header
		for seqTech in seqTechs:
			if seqTech in header:
				field(entry.Key,seqTech).Content = "yes"
				seqTechID = True
		if not seqTechID:
			field(entry.Key,"Other").Content = "yes"
		bns.Database.Db.Fields.Save()
		
			
