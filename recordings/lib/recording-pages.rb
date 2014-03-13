class RecordingPages < Nanoc::DataSource
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

			puts "datasource adding item for thumb"
			items << Nanoc::Item.new(
				"=render '_talk'",
				talk,
				"/talk/#{talk[:id]}/thumb.png/")
		end


		return items
	end
end
