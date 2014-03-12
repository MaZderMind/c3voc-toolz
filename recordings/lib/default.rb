# All files in the 'lib' directory will be loaded
# before nanoc starts compiling.

include Nanoc::Helpers::LinkTo
include Nanoc::Helpers::Rendering

class String
	def slugify()
		return self.downcase.gsub(/[\s\.\/_]/, ' ').squeeze(' ').strip.tr(' ', '-')
	end
end
