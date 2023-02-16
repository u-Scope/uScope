#!/bin/bash

#output directory
dist_dir="/home/result_btrfs_ebpf/"
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

fs="btrfs"
node_size_list=(16384 4096 65536)
datacow_list=(nodatacow datacow)
datasum_list=(nodatasum datasum)
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
	for datacow in "${datacow_list[@]}"
	do
	for datasum in "${datasum_list[@]}"
	do
	for node_size in "${node_size_list[@]}"
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
		
		echo "mkfs.btrfs /dev/${nvme_dev} -n ${node_size}"
		sudo mkfs.btrfs  /dev/${nvme_dev} -n ${node_size}
		echo "mount /dev/${nvme_dev} /nvme -o ${datacow},${datasum}"
		sudo mount /dev/${nvme_dev} /nvme  -o ${datacow},${datasum}
		echo "load success!"
		echo "sudo filebench -f ${workload_dir}/${workload_name_Fileserver} > ${dist_dir}/${fs}/${fs}_n${node_size}_t${type}_${datacow}_${datasum}_fileserver_${count}.txt"
		sudo filebench -f ${workload_dir}/${workload_name_Fileserver} > ${dist_dir}/${fs}/${fs}_n${node_size}_t${type}_${datacow}_${datasum}_fileserver_${count}.txt
		echo "sudo filebench -f ${workload_dir}/${workload_name_Webserver} > ${dist_dir}/${fs}/${fs}_n${node_size}_t${type}_${datacow}_${datasum}_webserver_${count}.txt"
		sudo filebench -f ${workload_dir}/${workload_name_Webserver} > ${dist_dir}/${fs}/${fs}_n${node_size}_t${type}_${datacow}_${datasum}_webserver_${count}.txt
		echo "sudo filebench -f ${workload_dir}/${workload_name_Varmail} > ${dist_dir}/${fs}/${fs}_n${node_size}_t${type}_${datacow}_${datasum}_varmail_${count}.txt"
		sudo filebench -f ${workload_dir}/${workload_name_Varmail} > ${dist_dir}/${fs}/${fs}_n${node_size}_t${type}_${datacow}_${datasum}_varmail_${count}.txt
		
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
