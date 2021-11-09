# FALCON Platform 

FALCON_VERSION = 1.0
export FALCON_VERSION

FALCON_DB98CX8580_32CD_PLATFORM = sonic-platform-db98cx8580-32cd-db98cx8580_$(FALCON_VERSION)_$(CONFIGURED_ARCH).deb
$(FALCON_DB98CX8580_32CD_PLATFORM)_SRC_PATH = $(PLATFORM_PATH)/sonic-platform-db98cx8580-32cd
$(FALCON_DB98CX8580_32CD_PLATFORM)_DEPENDS += $(LINUX_HEADERS) $(LINUX_HEADERS_COMMON)
$(FALCON_DB98CX8580_32CD_PLATFORM)_PLATFORM = x86_64-marvell_db98cx8580_32cd-r0 

SONIC_DPKG_DEBS += $(FALCON_DB98CX8580_32CD_PLATFORM)

