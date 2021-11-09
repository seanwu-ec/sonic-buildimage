# linux kernel package for marvell modules

# Add platform specific MOD
LINUX_KERNEL_MOD = linux-module-1.0.0-amd64.deb
$(LINUX_KERNEL_MOD)_URL = https://github.com/Marvell-switching/sonic-marvell-binaries/raw/master/amd64/kernel/$(LINUX_KERNEL_MOD)
SONIC_ONLINE_DEBS += $(LINUX_KERNEL_MOD)
