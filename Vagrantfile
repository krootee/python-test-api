Vagrant.configure("2") do |config|
	config.vm.box = "docker-ubuntu-1510-vision"
	config.vm.box_url = "http://cloud-images.ubuntu.com/vagrant/wily/current/wily-server-cloudimg-amd64-vagrant-disk1.box"
	config.vm.hostname = "google-vision-api-test"
	# Uncomment next line if you want to run multiple Vagrant VMs
	#config.vm.network "private_network", ip: "192.168.111.201"

	config.vm.provider "virtualbox" do |vb|
		# Increase VM memory to 2GB
		vb.customize ["modifyvm", :id, "--memory", "2048"]
	end
end