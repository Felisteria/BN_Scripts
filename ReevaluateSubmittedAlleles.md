---
title: "ReevaluateSubmittedAlleles"
date: 2019-04-19T14:40:00+01:00
draft: false
author: "Katleen Vranckx"
scriptlanguage: "py"
---


Reevaluates new alleles in selected entries against current wgMLST settings (consensus calling of multiple alleles and submission criteria). 
Alleles previously submitted but no longer meeting the criteria are removed and alleles meeting the criteria are submitted. 
The results are the same as if the entry had been orginally submitted with these criteria with the exception of the blast score of the removed alleles, as this score is not stored after submission. Instead, the identity threshold is filled in.
The script obtains all settings from the WGS tools plugin settings and also uses information stored in the experiment attachments. 
It can therefore only be run in the database where the blast allele calling job results has been imported to. Any export-import routines into another database removes the necessary data.
It can be run either by installing it in the database 'Install/remove plugin > Database functionality > Add > Browse to the script'. After closing and reopening the database, an additional menu item is available: 'WGS tools> Redo submission of new alleles for selected entries'
It can also be run using 'Scripts > Run script from file' and browse to the script. 


