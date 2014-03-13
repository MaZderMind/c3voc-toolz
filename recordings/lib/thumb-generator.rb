class ThumbGenerator < Nanoc::Filter
	identifier :generate_thumb
	type :text => :binary

	def run(content, params={})
		puts "thumbnail generator called with input"+content+" and writing to file"
		File.open(output_filename, 'w') do |file|
			file.write("png binary thumb")
		end
	end
end
