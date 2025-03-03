# μScope: Evaluating Storage Stack Robustness against Fail-slow Devices

The repository includes the following artifacts:

```eBPF Monitoring System``` : The source code of eBPF Monitoring System to observe the performance of the I/O excution in kernel.

```Filebench and Workload``` : The source code of modified Filebench(based on [filebench/filebench](https://github.com/filebench/filebench) and three Workloads.

```Example of results``` : The examples of results from filebench and eBPF monitoring.


## How to execute performance test:


### Setp 1: Install Filebench:

```
cd ./filebench-new
./configure
sudo make
sudo make install
echo 0 > /proc/sys/kernel/randomize_va_space
filebench -f ./workloads/fileserver.f
```

If filebench runs normally and outputs results every 5 seconds, it works.

### Setp 2: Set Kernel Config:

First you should enter the main directory of system source code, and then

```
sudo make menuconfig
```

Set the Device Drivers -> Block devices -> RAM block device support to "M".
And then save changes to .config.

Next, replace (source code)/drivers/block/loop.c by kernel-change/loop.c in this repository.
replace (source code)/drivers/block/brd.c by brd.c in this repository.

After that, re-compile the system kernel.

```
sudo make -j8
make modules_install
make install
reboot
```


### Setp 3: Necessary installation for Device Simulation:

First install nvme-loop module and try to simulate. 
In the command /path/to/nvme should be replaced by user.

```
sudo apt-get install nvme-loop

sudo modprobe nvme-loop

dd if=/dev/zero of=/path/to/nvme bs=1M count=1000

losetup -f /path/to/nvme
```

Second install tools--configshell-fb and NVME Target CLI.

```
pip install configshell-fb

git clone git://git.infradead.org/users/hch/nvmetcli.git
```

Then change the content of  nvmetcli/examples/loop.json from "path": "/dev/nvme0n1" to "path": "/dev/loop0".

Next generate and link nvme target.

```
./nvmetcli restore examples/loop.json

nvme connect -t loop -n testnqn -q hostnqn

```

Final we can check by 
```
nvme list
```

If the loop device is listed, it works.


### Setp 4: Custom Settings:

Settings in the script shoule be set ahead of run:

```
#output directory
dist_dir="/home/result_ext4_ebpf/"
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
```

The parameters of tests can also be adjusted:
```
fs="ext4"
block_size_list=(4096 1024 2048)
inode_size_list=(256 128 512 1024)
journal_mode_list=(journal ordered writeback)
percent_list=(10)
delay_list=(10)
type_list=(0 1 2 3)
```
### Setp 5: Run the test:

There are two ways to run the test.
First of all, make sure all module is unloaded ahead of run because they will be loaded with different parameters during running.

1.Use the scripts which combines eBPF monitoring system and workload together.
```
./eBPF/ebpf_filebench_ext4.sh
./eBPF/ebpf_filebench_btrfs.sh
./eBPF/ebpf_filebench_xfs.sh
./eBPF/ebpf_filebench_f2fs.sh
```

2.Run the eBPF monitoring system and then load the workload. In this way the process can be stopped at any time.
```
sudo python ./eBPF/loop_ext4.py
sudo ./filebench_ext4.sh
#stop
sudo killall python
```





