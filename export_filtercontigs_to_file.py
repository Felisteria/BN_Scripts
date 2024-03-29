#//$menu window=main;popup=Scripts;name=Export contigs ...; 
import bns
import os

toRemove = ["n"] # contigs consisting only of elements in this string will be removed from the export, add in small caps
dialog = bns.Windows.XmlDlgBuilder
MessageBox 	= bns.Util.Program.MessageBox
fld2filename = "identifier" #the script can use either the key or a field as the file name for the exported fasta, when using a field, verify the content is unique and uncomment the marked line

class FileSelectDlg(dialog.Dialogs):
	def __init__(self):
		dialog.Dialogs.__init__(self, 'DialogExportSeq')
		self.folderName = ""
		self.exptype = ""
		#TODO: use view, because sometimes there are more elements selected and you dont see them
		ot = bns.Database.Db.Entries.ObjectType
		viewSelectedEntries = ot.GetViewSelectedContent(ot.GetCurrentViewID())
		self.selectedEntries = [x for x in bns.Database.Db.Selection if x.Key in viewSelectedEntries]
		if len(self.selectedEntries) == 0:
			raise RuntimeError("Warning", "No entry selected.")
		e = bns.Database.Db.ExperimentTypes
		self.experiments = [x for x in e if x.Class=='SEQ']
		self.experiments_names = [exp.DispName for exp in self.experiments]
		n = min(4,len(self.experiments))
		self.fieldExp = dialog.Drop('exps',self.experiments_names,n,30)
		self.fieldOutputFolder = dialog.File('f2', [], 30, "Select a folder",
		                          isdir=True)
		grid = [["Output folder:", self.fieldOutputFolder],
						["Experiment:", self.fieldExp]]
		simple = dialog.SimpleDialog(grid,onOk=self.onOk)
		self.AddSimpleDialog("Export contig sequences of the selected entries", simple)

	def onOk(self, args):
		self.folderName = self.fieldOutputFolder.GetValue()
		self.exptype = self.fieldExp.GetValue()
		

	def export(self):
		for entry in self.selectedEntries:
#			uncomment the line below and comment the next line to use a field for the file name			
#			name = entry.Field(fld2filename).Content 
			name = entry.Key
			seqData = bns.Sequences.SequenceData(entry.Key,self.exptype)
			thisSeq = seqData.LoadSequence().split('|')
			fname = os.path.join(self.folderName,name +'_'+self.exptype+'.fasta')
			with open(fname,'w') as f:
				i = 1
				for s in thisSeq:
					countRemove = 0
					for c in toRemove:
						countRemove = countRemove + s.count(c)
					if countRemove == len(s):
						continue
					f.write(">%s_%s_%s\n" % (i,entry.Key,self.exptype))
					f.write("%s\n" % (s))
					i+=1
	
dlg = FileSelectDlg()
if dlg.Show():
	dlg.export()





