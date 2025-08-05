#!/bin/bash

# Usage: sudo ./format_zynq_sd.sh /dev/sdX SERIAL_NUMBER
# Example: sudo ./format_zynq_sd.sh /dev/sdb 3001

set -e

DEVICE=$1
SERIAL_NUM=$2

if [ -z "$DEVICE" ] || [ -z "$SERIAL_NUM" ]; then
    echo "Usage: sudo $0 /dev/sdX SERIAL_NUMBER"
    echo "Example: sudo $0 /dev/sdb 3001"
    exit 1
fi

if [ ! -b "$DEVICE" ]; then
    echo "Error: $DEVICE is not a block device."
    exit 2
fi

# Look up MAC address from CSV file
MAC_ADDRESS=$(awk -F' ' -v serial="$SERIAL_NUM" '$1==serial && $2=="eth0" {print $4}' ../mac_addr.csv)

if [ -z "$MAC_ADDRESS" ]; then
    echo "Error: Could not find MAC address for serial number $SERIAL_NUM"
    exit 4
fi

echo "Found MAC address: $MAC_ADDRESS for serial number $SERIAL_NUM"

echo "WARNING: This will ERASE ALL DATA on $DEVICE"
read -p "Type YES to continue: " CONFIRM
if [ "$CONFIRM" != "YES" ]; then
    echo "Aborted."
    exit 3
fi

echo "Unmounting any mounted partitions on $DEVICE..."
sudo umount ${DEVICE}?* || true

echo "Wiping partition table on $DEVICE..."
sudo dd if=/dev/zero of=$DEVICE bs=1M count=10

echo "Creating new msdos partition table..."
sudo parted -s $DEVICE mklabel msdos

echo "Creating 1GiB BOOT partition starting at 4MiB..."
sudo parted -s -a optimal $DEVICE mkpart primary fat32 4MiB 1028MiB
sudo parted -s $DEVICE set 1 boot on

echo "Creating rootfs partition from 1028MiB to end..."
sudo parted -s -a optimal $DEVICE mkpart primary ext4 1028MiB 100%

BOOT_PART=${DEVICE}1
ROOT_PART=${DEVICE}2

echo "Formatting BOOT partition as FAT32..."
sudo mkfs.vfat -F 32 -n BOOT $BOOT_PART

echo "Formatting rootfs partition as ext4..."
sudo mkfs.ext4 -F -L rootfs $ROOT_PART

echo ""
echo "SD card formatted for ZYNQ:"
echo "  - 4MiB empty space"
echo "  - BOOT partition (FAT32, 1GiB): $BOOT_PART"
echo "  - rootfs partition (ext4, ~31GiB): $ROOT_PART"

BOOT_MNT=/mnt/boot
ROOT_MNT=/mnt/root

echo "Mounting partitions..."
sudo mount $BOOT_PART $BOOT_MNT
sudo mount $ROOT_PART $ROOT_MNT

echo "Copying files into BOOT partition..."
sudo cp -r boot/* $BOOT_MNT
sudo echo "$MAC_ADDRESS" > $BOOT_MNT/eth1_mac.dat
echo "Copying OS into ROOTFS partition..."
sudo tar -xf alma8_rev2a_xczu7ev_sd-*.tar.xz -C $ROOT_MNT
echo "Copying files into ROOTFS partition..."
sudo cp -r rootfs/soft $ROOT_MNT/root

MOUNT_POINT=$ROOT_MNT

echo "Done copying. Waiting until it is safe to unmount $MOUNT_POINT..."

while true; do
    # Check if any process has open file handles on the SD card
    if lsof +D "$MOUNT_POINT" &>/dev/null; then
        sleep 1
        continue
    fi

    # Flush all pending writes to disk
    sync

    # Try a dry-run unmount using `umount --fake` if available
    if umount "$MOUNT_POINT" --fake &>/dev/null; then
        break
    else
        sleep 1
    fi
done

sudo umount $BOOT_MNT
sudo umount $ROOT_MNT

echo "SD card is unmounted. You can extract it now."