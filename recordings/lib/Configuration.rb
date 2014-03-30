class Configuration
	@@events = [
		{
			:schedule => 'http://www.fossgis.de/konferenz/2010/schedule.de.xml',
			# no videos, only attachments
		},

		{
			# the pentabarf-xml is taken to build a person-, event- and talk-index
			# attachments from the pentabarf are displayed for download
			:schedule => 'http://www.fossgis.de/konferenz/2011/programm/schedule.de.xml',

			# base path to media index (Any HTML-Page or Textfile listing the Filenames is fine, Apache Autoindex works perfectly)
			:media_listing => 'http://ftp5.gwdg.de/pub/misc/openstreetmap/FOSSGIS2011/',

			# this regex is used to find filenames in the above listing
			# the first subpart-match is used to assign the filename to an event-id
			# filetype is determined by file-extension and assigned to either a video-player,
			# an audio-player or as additions to the download-section
			:filename_regex => /href="(FOSSGIS2011-([0-9]+)[^"]+)"/
		},

		{
			:schedule => 'http://www.fossgis.de/konferenz/2012/programm/schedule.de.xml',
			:media_listing => 'http://ftp5.gwdg.de/pub/misc/openstreetmap/FOSSGIS2012/',
			:filename_regex => /href="(FOSSGIS2012-([0-9]+)[^"]+)"/
		},

		{
			:schedule => 'http://www.fossgis.de/konferenz/2013/programm/schedule.de.xml',
			:media_listing => 'http://ftp5.gwdg.de/pub/misc/openstreetmap/FOSSGIS2013/',
			:filename_regex => /href="(FOSSGIS(?:20)?13-([0-9]+)[^"]+)"/
		},

		{
			:schedule => 'http://www.fossgis.de/konferenz/2014/programm/schedule.de.xml',
			:media_listing => 'http://ftp5.gwdg.de/pub/misc/openstreetmap/FOSSGIS2014/',
			:filename_regex => /href="(([0-9]+)[^"]+)"/
		}
	]


	def self.events
		@@events
	end
end
