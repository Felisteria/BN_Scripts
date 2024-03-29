from Bio import SeqIO
import os

inputfolder = "full path to folder with Genbank files"
outputfolder = "full path to folder to store output fastas"

for gb in os.listdir(inputfolder):
	gbpath = os.path.join(inputfolder, gb)
	fastapath = os.path.join(outputfolder, gb + ".fna")
	if os.path.isfile(gbpath):
		SeqIO.convert(gbpath, "genbank", fastapath, "fasta")
