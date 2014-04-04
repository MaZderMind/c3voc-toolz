class PageGenerator < Nanoc::DataSource
	identifier :schedule

	def items
		items = []


		Schedule.events().each do |event|
			items << Nanoc::Item.new(
				"=render '_event'",
				event,
				"/event/#{event[:title].slugify}/")
		end

		Schedule.talks().each do |talk|
			items << Nanoc::Item.new(
				"=render '_talk'",
				talk,
				"/talk/#{talk[:id]}/")

			if talk[:files]
				talk[:files].each do |url|
					if ['.mp4', '.webm', '.mov'].include?(File.extname(url))
						items << Nanoc::Item.new(
							url,
							talk,
							"/talk/#{talk[:id]}/thumb.png/",
							{:mtime => DateTime.new(2000, 1, 1), :checksum => url.checksum })

						break

					end
				end
			end
		end


		return items
	end
end
