require 'shellwords'

class ThumbGenerator < Nanoc::Filter
	identifier :generate_thumb
	type :text => :binary

	def run(url, params={})
		puts "\tgenerating thumbnail\t".green+" #{url}"

		system("avconv -i #{url.shellescape} -ss 20 -frames:v 1 -vf scale='iw*sar:ih' -f image2 -c png #{output_filename.shellescape} >/dev/null 2>&1")
	end
end
