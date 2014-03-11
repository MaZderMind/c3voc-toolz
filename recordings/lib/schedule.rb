class String
	def slugify()
		return self.downcase.gsub(/[\s\.\/_]/, ' ').squeeze(' ').strip.tr(' ', '-')
	end
end

class Events
	@@events = {
		'FOSSGIS2010' => {
			:schedule => 'http://www.fossgis.de/konferenz/2010/schedule.de.xml',
			# no videos, only attachments
		},

		'FOSSGIS2011' => {
			# the pentabarf-xml is taken to build a person-, event- and talk-index
			# attachments from the pentabarf are displayed for download
			:schedule => 'http://www.fossgis.de/konferenz/2011/programm/schedule.de.xml',

			# base path to media index (Any HTML-Page or Textfile listing the Filenames is fine, Apache Autoindex works perfectly)
			:media_listing => 'http://ftp5.gwdg.de/pub/misc/openstreetmap/FOSSGIS2011/',

			# this regex is used to find filenames in the above listing
			# the first subpart-match is used to assign the filename to an event-id
			# filetype is determined by file-extension and assigned to either a video-player,
			# an audio-player or as additions to the download-section
			:filename_regex => 'FOSSGIS2011-([0-9]{3}).*'
		},

		'FOSSGIS2012' => {
			:schedule => 'http://www.fossgis.de/konferenz/2012/programm/schedule.de.xml',
			:media_listing => 'http://ftp5.gwdg.de/pub/misc/openstreetmap/FOSSGIS2012/',
			:filename_regex => 'FOSSGIS2012-([0-9]{3}).*'
		},

		'FOSSGIS2013' => {
			:schedule => 'http://www.fossgis.de/konferenz/2013/programm/schedule.de.xml',
			:media_listing => 'http://ftp5.gwdg.de/pub/misc/openstreetmap/FOSSGIS2013/',
			:filename_regex => 'FOSSGIS(?20)?12-([0-9]{3}).*'
		},

		'FOSSGIS2014' => {
			:schedule => 'http://www.fossgis.de/konferenz/2014/programm/schedule.de.xml'
			#:media_listing => 'http://ftp5.gwdg.de/pub/misc/openstreetmap/FOSSGIS2014/'
			#:filename_regex => 'FOSSGIS(?20)?12-([0-9]{3}).*'
		}
	}

	def self.names
		return @@events.keys()
	end
end
