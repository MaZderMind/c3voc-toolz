Pentabarf-Based Media-to-Auphonic-Uploader
==========================================

 1. Reads the schedule.xml provided via `--schedule`
 1. Reads auphonic-login-data as "username:password" from the file named via --auphonic-login (defailts to `$HOME/.auphonic-login`)
 2. Monitors the recordings-folder mentioned with `--recordings`
 3. Looks for files in that folder with names starting by one of the talk-ids (ie. `365-a-very-cool-talk.ogv` will be associated with th talk no. 365)
 4. Uploads those files to auphonic using the metadata taken from the schedule
 5. Moves files uploaded completely to the a folder named with `--finished` (defaults to a subfolder `finished` inside the recordings-folder)
 5. Sleeps when no more Files are found
