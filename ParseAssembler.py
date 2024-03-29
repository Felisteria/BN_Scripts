#Script to extract the assembler and version used for the most recent de novo assembly
#Script written by Katleen Vranckx for own use based on script extract_duration_CE_latest_log from Jan Deneweth

import bns
from datetime import datetime


# Global variables, adapt to your database
INFOFIELD_NAME = "de novo assembler"

# DO not change beyond this line, unless you know what you are doing!
def check_assembler(log):
	assemblers = ["unicycler" , "SPAdes version: 3.13.1" , "SPAdes version: 3.7.1" , "skesa" , "velvet"]
	for assembler in assemblers:
		if assembler in log:
			return assembler

# Process all selected entries
for entry in bns.Database.Db.Selection:
	
	# Iterate all CE log attachments
	attachments = entry.GetAttachmentList()
	latest = None
	
	assembler = None
	for log in attachments:
		if 'detailed log for job with ID' in log['Description']:
			content = log['Attach'].Content
			if "DeNovoAssembler" in content:
				if "Computation finished" in content: #only consider logs of succesfully run and finished assemblies
					line = content.splitlines()[1]
					try:
						timestamp, msg_type, msg = line.split('\t', 2) # If this gives error, too few tabs => malformed log
					except ValueError:
						continue
					if latest is None:
						assembler = check_assembler(content)
						latest = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
					else:#more than one de novo log present, check the most recent finished one
						timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
						if timestamp > latest:
							assembler = check_assembler(content)
					
			
	# Update the entry infofield
#	try:
#		entry.Field(INFOFIELD_NAME).Content = assembler or ''
#	except:
	for field in bns.Database.Db.Fields:
		if field.DispName == INFOFIELD_NAME:
			entry.Field(field.ID).Content = assembler or ''
			break
	else:
		
		entry.Field(INFOFIELD_NAME).Content = assembler or ''
		
		


# Save all updated fields
bns.Database.Db.Fields.Save()


#
#
# END OF FILE
