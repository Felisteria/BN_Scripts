#Script to extract build number of CE used to for the most recent de novo assembly
#Script written by Katleen Vranckx for own use based on script extract_duration_CE_latest_log from Jan Deneweth

import bns
from datetime import datetime


# Global variables
INFOFIELD_NAME = "ce_build"


# Process all selected entries
for entry in bns.Database.Db.Selection:
	
	# Iterate all CE log attachments
	attachments = entry.GetAttachmentList()
	latest = None
	cebuild = None
	for log in attachments:
		if 'detailed log for job with ID' in log['Description']:
			content = log['Attach'].Content
			if "DeNovoAssembler" in content:

				line = content.splitlines()[1]

				try:
					timestamp, msg_type, msg = line.split('\t', 2) # If this gives error, too few tabs => malformed log
				except ValueError:
					continue
				if latest is None:
					cebuild = msg.split('(')[1].strip(')')
					latest = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
				else:#more than one de novo log present, check the most recent one
					timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
					if timestamp > latest:
						cebuild = msg.split('(')[1].strip(')')
					
			
	# Update the entry infofield
	entry.Field(INFOFIELD_NAME).Content = cebuild or ''


# Save all updated fields
bns.Database.Db.Fields.Save()


#
#
# END OF FILE
