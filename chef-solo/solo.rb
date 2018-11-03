root = File.absolute_path(File.dirname(__FILE__))

file_cache_path File.join(root, 'chef-cache')
cookbook_path File.join(root, 'cookbooks')
