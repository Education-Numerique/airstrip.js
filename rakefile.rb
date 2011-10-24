require 'yaml'

@config = YAML.load_file("config.yaml")
@config['platform'] = "dev" if ENV['PLATFORM'].nil?

PROJECT_NAME = File.basename(File.dirname(__FILE__))

DIST_PATH = File.join(@config[@config['platform']]['deploy'], PROJECT_NAME)



task :default => [:deploy]

task :deploy do
	desc("Deploying static stuff")
	p DIST_PATH
	mkdir_p DIST_PATH
	cp_r FileList.new('src/*'), DIST_PATH
end
