#!/bin/bash

#output directory
dist_dir="/home/result_xfs_ebpf/"
#test dev
nvme_dev="nvme0n1"
nvme_name="nvme0"
#workload directory
workload_dir="/home/filebench-new/workloads"
#workload names
workload_name_Fileserver="new_fileserver.f"
workload_name_Webserver="new_webserver.f"
workload_name_Varmail="new_varmail.f"
#nvmetcli directory
nvmetcli_dir="/home/nvmetcli"

fs="xfs"
block_size_list=(4096 1024 2048)
inode_size_list=(256 128 512 2048)
allocation_group_count_list=(8 32 128)
type_list=(0 1 2 3)


if [ ! -d ${dist_dir} ];then
    mkdir ${dist_dir}
fi

if [ ! -d ${dist_dir}/${fs} ];then
    mkdir ${dist_dir}/${fs}
fi

sudo modprobe nvme-loop
echo 0 > /proc/sys/kernel/randomize_va_space

for type in "${type_list[@]}"
do
	for block_size in "${block_size_list[@]}"
	do
	for allocation_group_count in "${allocation_group_count_list[@]}"
	do
	for inode_size in "${inode_size_list[@]}"
	do
	for count in {1..10..1}
	do
		echo "modprobe loop type=${type}"
		sudo modprobe loop type=${type}
		sudo modprobe brd rd_nr=1 rd_size=29360128
		sudo losetup -f /dev/ram0
		echo "${nvmetcli_dir}/nvmetcli restore ${nvmetcli_dir}/examples/loop.json"
		sudo ${nvmetcli_dir}/nvmetcli restore ${nvmetcli_dir}/examples/loop.json
		echo "nvme connect -t loop -n testnqn -q hostnqn"
		sudo nvme connect -t loop -n testnqn -q hostnqn
		
		echo "mkfs.xfs  /dev/${nvme_dev} -b size=${block_size} -d agcount=${allocation_group_count} -i size=${inode_size}"
		sudo mkfs.xfs  /dev/${nvme_dev} -b size=${block_size}  -d agcount=${allocation_group_count} -i size=${inode_size}
		echo "mount /dev/${nvme_dev} /nvme"
		sudo mount /dev/${nvme_dev} /nvme
		echo "load success!"
		echo "sudo filebench -f ${workload_dir}/${workload_name_Fileserver} > ${dist_dir}/${fs}/${fs}_b${block_size}_i${inode_size}_ac${allocation_group_count}_t${type}_fileserver_${count}.txt"
		sudo filebench -f ${workload_dir}/${workload_name_Fileserver} > ${dist_dir}/${fs}/${fs}_b${block_size}_i${inode_size}_ac${allocation_group_count}_t${type}_fileserver_${count}.txt
		echo "sudo filebench -f ${workload_dir}/${workload_name_Webserver} > ${dist_dir}/${fs}/${fs}_b${block_size}_i${inode_size}_ac${allocation_group_count}_t${type}_webserver_${count}.txt"
		sudo filebench -f ${workload_dir}/${workload_name_Webserver} > ${dist_dir}/${fs}/${fs}_b${block_size}_i${inode_size}_ac${allocation_group_count}_t${type}_webserver_${count}.txt
		echo "sudo filebench -f ${workload_dir}/${workload_name_Varmail} > ${dist_dir}/${fs}/${fs}_b${block_size}_i${inode_size}_ac${allocation_group_count}_t${type}_varmail_${count}.txt"
		sudo filebench -f ${workload_dir}/${workload_name_Varmail} > ${dist_dir}/${fs}/${fs}_b${block_size}_i${inode_size}_ac${allocation_group_count}_t${type}_varmail_${count}.txt
		
		sudo umount /dev/${nvme_dev}
		sudo nvme disconnect -d /dev/${nvme_name}
		sudo ${nvmetcli_dir}/nvmetcli clear
		sudo losetup -d /dev/loop0
		sudo rmmod loop
		sudo rmmod brd
		echo "unload completely"
	done
	done
	done
	done
done
