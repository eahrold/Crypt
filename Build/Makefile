include /usr/local/share/luggage/luggage.make

TITLE=Crypt_Client
PACKAGE_NAME=Crypt_Client
REVERSE_DOMAIN=com.grahamgilbert
PAYLOAD=\
			pack-csfde \
			pack-crypt \
			pack-Library-LaunchDaemons-com.grahamgilbert.crypt.needsescrow.plist

pack-csfde: l_usr_local_bin
		@sudo ${CP} csfde ${WORK_D}/usr/local/bin/csfde
		@sudo chown root:wheel ${WORK_D}/usr/local/bin/csfde
		@sudo chmod 755 ${WORK_D}/usr/local/bin/csfde
		
pack-crypt: l_usr_local
		@sudo mkdir -p ${WORK_D}/usr/local/crypt
		@sudo ${CP} -R "Crypt.app" ${WORK_D}/usr/local/crypt/"Crypt.app"
		@sudo ${CP} -R "delayed_escrow" ${WORK_D}/usr/local/crypt/delayed_escrow
		@sudo chown -R root:wheel ${WORK_D}/usr/local/crypt
		@sudo chmod 755 ${WORK_D}/usr/local/crypt/delayed_escrow
		@sudo chmod 755 ${WORK_D}/usr/local/crypt/"Crypt.app"