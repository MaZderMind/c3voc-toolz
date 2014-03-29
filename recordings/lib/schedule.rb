require 'open-uri'
require 'nokogiri'
require 'colored'

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

				open(event[:schedule]) do |f|
					xml = Nokogiri::XML(f)

					# todo capture eventinfo
					xml.xpath('/schedule/conference').tap do |conference|
						event.merge!({
							:title => conference.xpath('title').text,
							:subtitle => conference.xpath('subtitle').text,
							:venue => conference.xpath('venue').text,
							:city => conference.xpath('city').text
						})
					end

					event[:talks] = Hash[xml.xpath('//event').map do |talk|
						[talk['id'].to_i, {
							:id => talk['id'],
							:title => talk.xpath('title').text,
							:subtitle => talk.xpath('subtitle').text,
							:abstract => talk.xpath('abstract').text,
							:description => talk.xpath('description').text,
							:persons => talk.xpath('persons/person').map do |person|
								{
									:id => person['id'],
									:name => person.text
								}
							end
						}]
					end]
				end

				if event[:media_listing] and event[:filename_regex]
					puts "\tfetching media-listing\t".green+" #{event[:media_listing]}"
					open(event[:media_listing]) do |f|
						media_listing = f.read

						media_listing.scan(event[:filename_regex]) do |fname, talkid|
							if event[:talks][talkid.to_i]
								if ! event[:talks][talkid.to_i][:files]
									event[:talks][talkid.to_i][:files] = {}
								end

								event[:talks][talkid.to_i][:files][ File.extname(fname) ] = File.join(event[:media_listing], fname)
							else
								puts talkid
							end

						end
					end
				end

				event[:talks] = event[:talks].values

			end
		end
	end
end
