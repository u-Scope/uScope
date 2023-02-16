#!/usr/bin/python
#
# disksnoop.py	Trace block device I/O: basic version of iosnoop.
#		For Linux, uses BCC, eBPF. Embedded C.
#
# Written as a basic example of tracing latency.
#
# Copyright (c) 2015 Brendan Gregg.
# Licensed under the Apache License, Version 2.0 (the "License")
#
# 11-Aug-2015	Brendan Gregg	Created this.

from __future__ import print_function
from bcc import BPF
from bcc.utils import printb
import os
import sys

REQ_WRITE = 1		# from include/linux/blk_types.h

# load BPF program
prog = """
#include <uapi/linux/ptrace.h>
#include <linux/blkdev.h>
#include <linux/bio.h>
#include <linux/fs.h>
#include <linux/path.h>
#include <linux/dcache.h>
#include <linux/genhd.h>
#include <linux/blk-mq.h>
#include <scsi/scsi_cmnd.h>

struct blxdata_t {
    u32 pid;
    u64 ts;
    char comm[TASK_COMM_LEN];
    char fucname[30];
    char signal[30];
    char Start;
};
BPF_PERF_OUTPUT(result);

BPF_HASH(start, struct request_queue *);



void trace_vfs_write_start(struct pt_regs *ctx,struct file *file, const char __user *buf, size_t count, loff_t *pos) {

	struct blxdata_t blxdata = {};
	blxdata.Start = 'S';
    	blxdata.pid = bpf_get_current_pid_tgid();
    	blxdata.ts = bpf_ktime_get_ns();
    	strcpy(blxdata.fucname, "vfs_write");
    	bpf_probe_read_kernel_str(&blxdata.signal,sizeof(blxdata.signal),file->f_path.dentry->d_name.name);
    	bpf_get_current_comm(&blxdata.comm, sizeof(blxdata.comm));
    	result.perf_submit(ctx, &blxdata, sizeof(blxdata));
}

void trace_vfs_write_completion(struct pt_regs *ctx,struct file *file, const char __user *buf, size_t count, loff_t *pos) {

	struct blxdata_t blxdata = {};
	blxdata.Start = 'E';
    	blxdata.pid = bpf_get_current_pid_tgid();
    	blxdata.ts = bpf_ktime_get_ns();
    	strcpy(blxdata.fucname, "vfs_write");
    	bpf_probe_read_kernel_str(&blxdata.signal,sizeof(blxdata.signal),file->f_path.dentry->d_name.name);
    	bpf_get_current_comm(&blxdata.comm, sizeof(blxdata.comm));
    	result.perf_submit(ctx, &blxdata, sizeof(blxdata));  	
}

void trace_generic_make_request_start(struct pt_regs *ctx,struct bio *bio) {

	struct blxdata_t blxdata = {};
	blxdata.Start = 'S';
    	blxdata.pid = bpf_get_current_pid_tgid();
    	blxdata.ts = bpf_ktime_get_ns();
    	strcpy(blxdata.fucname, "generic_make_request");
    	bpf_get_current_comm(&blxdata.comm, sizeof(blxdata.comm));
    	result.perf_submit(ctx, &blxdata, sizeof(blxdata));
}

void trace_generic_make_request_completion(struct pt_regs *ctx,struct bio *bio) {

	struct blxdata_t blxdata = {};
	blxdata.Start = 'E';
    	blxdata.pid = bpf_get_current_pid_tgid();
    	blxdata.ts = bpf_ktime_get_ns();
    	strcpy(blxdata.fucname, "generic_make_request");
    	bpf_get_current_comm(&blxdata.comm, sizeof(blxdata.comm));
    	result.perf_submit(ctx, &blxdata, sizeof(blxdata));
}

void trace_nvme_loop_queue_rq_start(struct pt_regs *ctx,struct blk_mq_hw_ctx *hctx, const struct blk_mq_queue_data *bd) {
	struct blxdata_t blxdata = {};
	blxdata.Start = 'S';
    	blxdata.pid = bpf_get_current_pid_tgid();
    	blxdata.ts = bpf_ktime_get_ns();
    	strcpy(blxdata.fucname, "nvme_loop_queue_rq");
    	bpf_get_current_comm(&blxdata.comm, sizeof(blxdata.comm));
    	result.perf_submit(ctx, &blxdata, sizeof(blxdata));
}

void trace_nvme_loop_queue_rq_completion(struct pt_regs *ctx,struct blk_mq_hw_ctx *hctx, const struct blk_mq_queue_data *bd) {

	struct blxdata_t blxdata = {};
	blxdata.Start = 'E';
    	blxdata.pid = bpf_get_current_pid_tgid();
    	blxdata.ts = bpf_ktime_get_ns();
    	strcpy(blxdata.fucname, "nvme_loop_queue_rq");
    	bpf_get_current_comm(&blxdata.comm, sizeof(blxdata.comm));
    	result.perf_submit(ctx, &blxdata, sizeof(blxdata));
}

void trace_nvme_loop_execute_work_start(struct pt_regs *ctx,struct work_struct *work) {
	struct blxdata_t blxdata = {};
	blxdata.Start = 'S';
    	blxdata.pid = bpf_get_current_pid_tgid();
    	blxdata.ts = bpf_ktime_get_ns();
    	strcpy(blxdata.fucname, "nvme_loop_execute_work");
    	bpf_get_current_comm(&blxdata.comm, sizeof(blxdata.comm));
    	result.perf_submit(ctx, &blxdata, sizeof(blxdata));
}

void trace_nvme_loop_execute_work_completion(struct pt_regs *ctx,struct work_struct *work) {

	struct blxdata_t blxdata = {};
	blxdata.Start = 'E';
    	blxdata.pid = bpf_get_current_pid_tgid();
    	blxdata.ts = bpf_ktime_get_ns();
    	strcpy(blxdata.fucname, "nvme_loop_execute_work");
    	bpf_get_current_comm(&blxdata.comm, sizeof(blxdata.comm));
    	result.perf_submit(ctx, &blxdata, sizeof(blxdata));
}
void trace_nvme_loop_complete_rq_start(struct pt_regs *ctx,struct request *req) {
	struct blxdata_t blxdata = {};
	blxdata.Start = 'S';
    	blxdata.pid = bpf_get_current_pid_tgid();
    	blxdata.ts = bpf_ktime_get_ns();
    	strcpy(blxdata.fucname, "nvme_loop_complete_rq");
    	bpf_get_current_comm(&blxdata.comm, sizeof(blxdata.comm));
    	result.perf_submit(ctx, &blxdata, sizeof(blxdata));
}

void trace_nvme_loop_complete_rq_completion(struct pt_regs *ctx,struct request *req) {

	struct blxdata_t blxdata = {};
	blxdata.Start = 'E';
    	blxdata.pid = bpf_get_current_pid_tgid();
    	blxdata.ts = bpf_ktime_get_ns();
    	strcpy(blxdata.fucname, "nvme_loop_complete_rq");
    	bpf_get_current_comm(&blxdata.comm, sizeof(blxdata.comm));
    	result.perf_submit(ctx, &blxdata, sizeof(blxdata));
}

void trace_nvme_loop_queue_response_start(struct pt_regs *ctx) {
	struct blxdata_t blxdata = {};
	blxdata.Start = 'S';
    	blxdata.pid = bpf_get_current_pid_tgid();
    	blxdata.ts = bpf_ktime_get_ns();
    	strcpy(blxdata.fucname, "nvme_loop_queue_response");
    	bpf_get_current_comm(&blxdata.comm, sizeof(blxdata.comm));
    	result.perf_submit(ctx, &blxdata, sizeof(blxdata));
}

void trace_nvme_loop_queue_response_completion(struct pt_regs *ctx) {

	struct blxdata_t blxdata = {};
	blxdata.Start = 'E';
    	blxdata.pid = bpf_get_current_pid_tgid();
    	blxdata.ts = bpf_ktime_get_ns();
    	strcpy(blxdata.fucname, "nvme_loop_queue_response");
    	bpf_get_current_comm(&blxdata.comm, sizeof(blxdata.comm));
    	result.perf_submit(ctx, &blxdata, sizeof(blxdata));
}

void trace_nvmet_bdev_execute_rw_start(struct pt_regs *ctx) {
	struct blxdata_t blxdata = {};
	blxdata.Start = 'S';
    	blxdata.pid = bpf_get_current_pid_tgid();
    	blxdata.ts = bpf_ktime_get_ns();
    	strcpy(blxdata.fucname, "nvmet_bdev_execute_rw");
    	bpf_get_current_comm(&blxdata.comm, sizeof(blxdata.comm));
    	result.perf_submit(ctx, &blxdata, sizeof(blxdata));
}

void trace_nvmet_bdev_execute_rw_completion(struct pt_regs *ctx) {

	struct blxdata_t blxdata = {};
	blxdata.Start = 'E';
    	blxdata.pid = bpf_get_current_pid_tgid();
    	blxdata.ts = bpf_ktime_get_ns();
    	strcpy(blxdata.fucname, "nvmet_bdev_execute_rw");
    	bpf_get_current_comm(&blxdata.comm, sizeof(blxdata.comm));
    	result.perf_submit(ctx, &blxdata, sizeof(blxdata));
}

void trace_loop_queue_rq_start(struct pt_regs *ctx) {
	struct blxdata_t blxdata = {};
	blxdata.Start = 'S';
    	blxdata.pid = bpf_get_current_pid_tgid();
    	blxdata.ts = bpf_ktime_get_ns();
    	strcpy(blxdata.fucname, "loop_queue_rq");
    	bpf_get_current_comm(&blxdata.comm, sizeof(blxdata.comm));
    	result.perf_submit(ctx, &blxdata, sizeof(blxdata));
}

void trace_loop_queue_rq_completion(struct pt_regs *ctx) {

	struct blxdata_t blxdata = {};
	blxdata.Start = 'E';
    	blxdata.pid = bpf_get_current_pid_tgid();
    	blxdata.ts = bpf_ktime_get_ns();
    	strcpy(blxdata.fucname, "loop_queue_rq");
    	bpf_get_current_comm(&blxdata.comm, sizeof(blxdata.comm));
    	result.perf_submit(ctx, &blxdata, sizeof(blxdata));
}

void trace_loop_queue_work_start(struct pt_regs *ctx) {
	struct blxdata_t blxdata = {};
	blxdata.Start = 'S';
    	blxdata.pid = bpf_get_current_pid_tgid();
    	blxdata.ts = bpf_ktime_get_ns();
    	strcpy(blxdata.fucname, "loop_queue_work");
    	bpf_get_current_comm(&blxdata.comm, sizeof(blxdata.comm));
    	result.perf_submit(ctx, &blxdata, sizeof(blxdata));
}

void trace_loop_queue_work_completion(struct pt_regs *ctx) {

	struct blxdata_t blxdata = {};
	blxdata.Start = 'E';
    	blxdata.pid = bpf_get_current_pid_tgid();
    	blxdata.ts = bpf_ktime_get_ns();
    	strcpy(blxdata.fucname, "loop_queue_work");
    	bpf_get_current_comm(&blxdata.comm, sizeof(blxdata.comm));
    	result.perf_submit(ctx, &blxdata, sizeof(blxdata));
}

void trace_lo_write_bvec_start(struct pt_regs *ctx) {
	struct blxdata_t blxdata = {};
	blxdata.Start = 'S';
    	blxdata.pid = bpf_get_current_pid_tgid();
    	blxdata.ts = bpf_ktime_get_ns();
    	strcpy(blxdata.fucname, "lo_write_bvec");
    	bpf_get_current_comm(&blxdata.comm, sizeof(blxdata.comm));
    	result.perf_submit(ctx, &blxdata, sizeof(blxdata));
}

void trace_lo_write_bvec_completion(struct pt_regs *ctx) {

	struct blxdata_t blxdata = {};
	blxdata.Start = 'E';
    	blxdata.pid = bpf_get_current_pid_tgid();
    	blxdata.ts = bpf_ktime_get_ns();
    	strcpy(blxdata.fucname, "lo_write_bvec");
    	bpf_get_current_comm(&blxdata.comm, sizeof(blxdata.comm));
    	result.perf_submit(ctx, &blxdata, sizeof(blxdata));
}

void trace_ext4_file_write_iter_start(struct pt_regs *ctx) {
	struct blxdata_t blxdata = {};
	blxdata.Start = 'S';
    	blxdata.pid = bpf_get_current_pid_tgid();
    	blxdata.ts = bpf_ktime_get_ns();
    	strcpy(blxdata.fucname, "ext4_file_write_iter");
    	bpf_get_current_comm(&blxdata.comm, sizeof(blxdata.comm));
    	result.perf_submit(ctx, &blxdata, sizeof(blxdata));
}

void trace_ext4_file_write_iter_completion(struct pt_regs *ctx) {

	struct blxdata_t blxdata = {};
	blxdata.Start = 'E';
    	blxdata.pid = bpf_get_current_pid_tgid();
    	blxdata.ts = bpf_ktime_get_ns();
    	strcpy(blxdata.fucname, "ext4_file_write_iter");
    	bpf_get_current_comm(&blxdata.comm, sizeof(blxdata.comm));
    	result.perf_submit(ctx, &blxdata, sizeof(blxdata));
}

"""
if __name__ == '__main__':
	b = BPF(text = prog)

	b.attach_kprobe(event="vfs_write", fn_name="trace_vfs_write_start")
	b.attach_kretprobe(event="vfs_write", fn_name="trace_vfs_write_completion")

	b.attach_kprobe(event="ext4_file_write_iter", fn_name="trace_ext4_file_write_iter_start")
	b.attach_kretprobe(event="ext4_file_write_iter", fn_name="trace_ext4_file_write_iter_completion")

	b.attach_kprobe(event="generic_make_request", fn_name="trace_generic_make_request_start")
	b.attach_kretprobe(event="generic_make_request", fn_name="trace_generic_make_request_completion")
	
	b.attach_kprobe(event="nvme_loop_queue_rq", fn_name="trace_nvme_loop_queue_rq_start")
	b.attach_kretprobe(event="nvme_loop_queue_rq", fn_name="trace_nvme_loop_queue_rq_completion")

	b.attach_kprobe(event="loop_queue_rq", fn_name="trace_loop_queue_rq_start")
	b.attach_kretprobe(event="loop_queue_rq", fn_name="trace_loop_queue_rq_completion")

	b.attach_kprobe(event="loop_queue_work", fn_name="trace_loop_queue_work_start")
	b.attach_kretprobe(event="loop_queue_work", fn_name="trace_loop_queue_work_completion")
	
	b.attach_kprobe(event="nvme_loop_complete_rq", fn_name="trace_nvme_loop_complete_rq_start")
	b.attach_kretprobe(event="nvme_loop_complete_rq", fn_name="trace_nvme_loop_complete_rq_completion")

	b.attach_kprobe(event="lo_write_bvec", fn_name="trace_lo_write_bvec_start")
	b.attach_kretprobe(event="lo_write_bvec", fn_name="trace_lo_write_bvec_completion")

	b.attach_kprobe(event="nvme_loop_queue_response", fn_name="trace_nvme_loop_queue_response_start")
	b.attach_kretprobe(event="nvme_loop_queue_response", fn_name="trace_nvme_loop_queue_response_completion")

	b.attach_kprobe(event="journal_commit_transaction", fn_name="trace_journal_commit_transaction_start")
	b.attach_kretprobe(event="journal_commit_transaction", fn_name="trace_journal_commit_transaction_completion")

	filename = sys.argv[1]
	print(filename)
	result_file = open(filename,'w')
	
	start = 0
	def print_event(cpu, blxdata, size):
	    global start
	    event = b["result"].event(blxdata)
	    ban_comm = ["python","gmain"]
	    if	event.comm not in ban_comm:
	    	result_file.write("%-16d  ;%-32s  ;%-6d  ;%-30s  ;%-3s  ;%-13s   \n" % (event.ts, event.comm, event.pid, event.fucname, event.Start, event.signal))
	b["result"].open_perf_buffer(print_event)
	while 1:
		try:
			b.perf_buffer_poll()
		except KeyboardInterrupt:
			exit()
		
		
