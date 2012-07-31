Exec {
	path => [
		'/usr/local/bin',
		'/opt/local/bin',
		'/usr/bin', 
		'/usr/sbin', 
		'/bin',
		'/sbin'
		],
	logoutput => true,
}



package { 'python2.7':
	ensure => present,
}

package { 'python2.7-dev':
	ensure => present,
}

package { 'python2.7-twisted':
	ensure => present,
}

package { 'python2.7-openssl':
	ensure => present,
}

package { 'python-pip':
	ensure => present,
}

package { 'twisted':
	ensure => latest,
	provider => 'pip',

	require => [
		Package['python-pip'],
		Package['python2.7-twisted']
	],
}

package { 'dpkg-dev':
	ensure => present,
}

package { 'debhelper':
	ensure => present,
}

file { '/usr/local/bin/822-date':
	ensure => file,
	source => '/vagrant/manifests/support/822-date.sh',
	mode => 755,
}

exec { 'crlf2cr /usr/local/bin/822-date':
	command = "sed --in-place 's/\r//' /usr/local/bin/822-date",

	require => [
		File['/usr/local/bin/822-date'],
	],
}

file { '/usr/bin/twistd2.7':
	ensure => link,
	source => '/usr/local/bin/twistd',
	require => [
		Package['twisted'],
	],	
}

file { '/opt/glass':
	ensure => directory,
	source => '/vagrant',
	recurse => true,
}

exec { 'python setup.py install':
	require => [
		File['/opt/glass'],
		Package['python2.7'],
	],
	cwd => '/opt/glass',
}

exec { 'tap2deb':
	command => 'tap2deb -t glass_server.tac -m "Nullable <teo@nullable.se>" -y python -d twisted-glass-server',
	require => [
		File['/opt/glass'],
		Package['twisted'],
		Package['dpkg-dev'],
		Package['debhelper'],
		Exec['crlf2cr /usr/local/bin/822-date'],
		Exec['python setup.py install'],
		],

	cwd => '/opt/glass',
}

exec { 'uninstall twisted-glass-server':
	command => 'apt-get remove twisted-glass-server -y',
	returns => [
		0,
		100,
	]
}

package { 'twisted-glass-server':
	ensure => latest,
	source => '/opt/glass/.build/twisted-glass-server_1.0_all.deb',
	provider => 'dpkg',

	require => [
		Exec['tap2deb'],
		Exec['uninstall twisted-glass-server'],
		],
}

service { 'twisted-glass-server':
	ensure => running,
	require => [
		Package['twisted-glass-server'],
		],
	hasstatus => false,
}