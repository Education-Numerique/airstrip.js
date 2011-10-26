require 'yaml'
@config = YAML.load_file("config.yaml")
ENV['PLATFORM'] = "dev" if ENV['PLATFORM'].nil?
@config['platform'] = ENV['PLATFORM']
DIST_PATH = @config[@config['platform']]['deploy']


task :default => [:deploy]

task :deploy do
	desc("Deploying static stuff")
	mkdir_p DIST_PATH
	cp_r FileList.new('src/*'), DIST_PATH
end
