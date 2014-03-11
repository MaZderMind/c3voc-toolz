require 'open-uri'
require 'nokogiri'
require 'colored'

class String
	def slugify()
		return self.downcase.gsub(/[\s\.\/_]/, ' ').squeeze(' ').strip.tr(' ', '-')
	end
end

class Schedule
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
			:filename_regex => 'FOSSGIS2011-([0-9]{3}).*'
		},

		{
			:schedule => 'http://www.fossgis.de/konferenz/2012/programm/schedule.de.xml',
			:media_listing => 'http://ftp5.gwdg.de/pub/misc/openstreetmap/FOSSGIS2012/',
			:filename_regex => 'FOSSGIS2012-([0-9]{3}).*'
		},

		{
			:schedule => 'http://www.fossgis.de/konferenz/2013/programm/schedule.de.xml',
			:media_listing => 'http://ftp5.gwdg.de/pub/misc/openstreetmap/FOSSGIS2013/',
			:filename_regex => 'FOSSGIS(?20)?12-([0-9]{3}).*'
		},

		{
			:schedule => 'http://www.fossgis.de/konferenz/2014/programm/schedule.de.xml'
			#:media_listing => 'http://ftp5.gwdg.de/pub/misc/openstreetmap/FOSSGIS2014/'
			#:filename_regex => 'FOSSGIS(?20)?12-([0-9]{3}).*'
		}
	]

	def self.events
		self.ensure_talks_loaded
		return @@events
	end

	def self.talks
		self.ensure_talks_loaded
		return @@events.map do |eventinfo|
			eventinfo[:talks]
		end.flatten(1)
	end

	def self.ensure_talks_loaded
		puts ""
		@@events.each do |event|
			if ! event[:talks]
				puts "\tfetching schedule\t".green+" #{event[:schedule]}"

				xml = Nokogiri::XML(open(event[:schedule]))

				# todo capture eventinfo
				xml.xpath('/schedule/conference').tap do |conference|
					event.merge!({
						:title => conference.xpath('title').text,
						:subtitle => conference.xpath('subtitle').text,
						:venue => conference.xpath('venue').text,
						:city => conference.xpath('city').text
					})
				end

				event[:talks] = xml.xpath('//event').map do |talk|
					{
						:id => talk['id'],
						:title => talk.xpath('title').text,
						:subtitle => talk.xpath('subtitle').text,
						:abstract => talk.xpath('abstract').text,
						:description => talk.xpath('description').text,
						:persons => talk.xpath('persons/person').map do |person|
							{:id => person['id'], :name => person.text}
						end
					}
				end

			end
		end
	end
end
