include /usr/local/share/luggage/luggage.make

TITLE=FileVault_Client
PACKAGE_NAME=FileVault_Client
REVERSE_DOMAIN=com.grahamgilbert
PAYLOAD=\
			pack-csfde \
			pack-fvserver

pack-csfde: l_usr_local_bin
		@sudo ${CP} csfde ${WORK_D}/usr/local/bin/csfde
		@sudo chown root:wheel ${WORK_D}/usr/local/bin/csfde
		@sudo chmod 755 ${WORK_D}/usr/local/bin/csfde
		
pack-fvserver: l_usr_local
		@sudo mkdir -p ${WORK_D}/usr/local/fvserver
		@sudo ${CP} -R "FileVault Server.app" ${WORK_D}/usr/local/fvserver/"FileVault Server.app"
		@sudo chown root:wheel ${WORK_D}/usr/local/fvserver/"FileVault Server.app"
		@sudo chmod 755 ${WORK_D}/usr/local/fvserver/"FileVault Server.app"