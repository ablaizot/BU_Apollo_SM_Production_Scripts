#!/bin/bash
set -e

DEVICE="$1"

# Validate input
if [[ -z "$DEVICE" || ! -b "$DEVICE" ]]; then
  echo "Usage: sudo $0 /dev/sdX"
  echo "Example: sudo $0 /dev/sdb"
  exit 1
fi

echo "WARNING: This will erase ALL data on $DEVICE. Continue? [y/N]"
read -r confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
  echo "Aborted."
  exit 1
fi

# Unmount existing partitions
echo "Unmounting existing partitions on $DEVICE..."
for part in $(ls ${DEVICE}?* 2>/dev/null); do
  sudo umount "$part" || true
done

# Wipe partition table
echo "Wiping partition table on $DEVICE..."
sudo dd if=/dev/zero of="$DEVICE" bs=1M count=10

# Create single ext4 partition
echo "Creating single ext4 partition..."
cat <<EOF | sudo sfdisk "$DEVICE"
label: dos
unit: sectors
${DEVICE}1 : start=2048, type=83
EOF

sleep 2  # Let the kernel update partition table

# Format as ext4
echo "Formatting ${DEVICE}1 as ext4..."
sudo mkfs.ext4 -F -L rootfs "${DEVICE}1"

echo "SSD is now formatted with a single ext4 partition labeled 'rootfs'."

ROOT_MNT=/mnt/ssd
echo "Mounting partitions..."
sudo mount ${DEVICE}1 $ROOT_MNT

echo "Copying OS onto SSD ..."
sudo tar -xf alma8_rev2a_xczu7ev_sd-*.tar.xz -C $ROOT_MNT

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

sudo umount $ROOT_MNT

echo "SSD is unmounted. You can extract it now."