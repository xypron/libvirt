#!/usr/bin/env python3

import argparse
import copy
import os
import re
import lxml.etree

import lark


def translate_vendor(name):
    T = {
        "CPUID_VENDOR_AMD": "AMD",
        "CPUID_VENDOR_INTEL": "Intel",
        "CPUID_VENDOR_HYGON": "Hygon",
    }

    if name in T:
        return T[name]

    print(f"warning: Unknown vendor '{name}'")
    return name


def translate_feature(name):
    T = {
        "CPUID_6_EAX_ARAT": "arat",
        "CPUID_7_0_EBX_ADX": "adx",
        "CPUID_7_0_EBX_AVX2": "avx2",
        "CPUID_7_0_EBX_AVX512BW": "avx512bw",
        "CPUID_7_0_EBX_AVX512CD": "avx512cd",
        "CPUID_7_0_EBX_AVX512DQ": "avx512dq",
        "CPUID_7_0_EBX_AVX512ER": "avx512er",
        "CPUID_7_0_EBX_AVX512F": "avx512f",
        "CPUID_7_0_EBX_AVX512IFMA": "avx512ifma",
        "CPUID_7_0_EBX_AVX512PF": "avx512pf",
        "CPUID_7_0_EBX_AVX512VL": "avx512vl",
        "CPUID_7_0_EBX_BMI1": "bmi1",
        "CPUID_7_0_EBX_BMI2": "bmi2",
        "CPUID_7_0_EBX_CLFLUSHOPT": "clflushopt",
        "CPUID_7_0_EBX_CLWB": "clwb",
        "CPUID_7_0_EBX_ERMS": "erms",
        "CPUID_7_0_EBX_FSGSBASE": "fsgsbase",
        "CPUID_7_0_EBX_HLE": "hle",
        "CPUID_7_0_EBX_INVPCID": "invpcid",
        "CPUID_7_0_EBX_MPX": "mpx",
        "CPUID_7_0_EBX_RDSEED": "rdseed",
        "CPUID_7_0_EBX_RTM": "rtm",
        "CPUID_7_0_EBX_SHA_NI": "sha-ni",
        "CPUID_7_0_EBX_SMAP": "smap",
        "CPUID_7_0_EBX_SMEP": "smep",
        "CPUID_7_0_EBX_TSC_ADJUST": "tsc_adjust",
        "CPUID_7_0_ECX_AVX512BITALG": "avx512bitalg",
        "CPUID_7_0_ECX_AVX512VNNI": "avx512vnni",
        "CPUID_7_0_ECX_AVX512_VBMI": "avx512vbmi",
        "CPUID_7_0_ECX_AVX512_VBMI2": "avx512vbmi2",
        "CPUID_7_0_ECX_AVX512_VPOPCNTDQ": "avx512-vpopcntdq",
        "CPUID_7_0_ECX_BUS_LOCK_DETECT": "bus-lock-detect",
        "CPUID_7_0_ECX_CLDEMOTE": "cldemote",
        "CPUID_7_0_ECX_GFNI": "gfni",
        "CPUID_7_0_ECX_LA57": "la57",
        "CPUID_7_0_ECX_MOVDIR64B": "movdir64b",
        "CPUID_7_0_ECX_MOVDIRI": "movdiri",
        "CPUID_7_0_ECX_PKU": "pku",
        "CPUID_7_0_ECX_RDPID": "rdpid",
        "CPUID_7_0_ECX_UMIP": "umip",
        "CPUID_7_0_ECX_VAES": "vaes",
        "CPUID_7_0_ECX_VPCLMULQDQ": "vpclmulqdq",
        "CPUID_7_0_EDX_AMX_BF16": "amx-bf16",
        "CPUID_7_0_EDX_AMX_INT8": "amx-int8",
        "CPUID_7_0_EDX_AMX_TILE": "amx-tile",
        "CPUID_7_0_EDX_ARCH_CAPABILITIES": "arch-capabilities",
        "CPUID_7_0_EDX_AVX512_4FMAPS": "avx512-4fmaps",
        "CPUID_7_0_EDX_AVX512_4VNNIW": "avx512-4vnniw",
        "CPUID_7_0_EDX_AVX512_FP16": "avx512-fp16",
        "CPUID_7_0_EDX_CORE_CAPABILITY": "core-capability",
        "CPUID_7_0_EDX_FSRM": "fsrm",
        "CPUID_7_0_EDX_SERIALIZE": "serialize",
        "CPUID_7_0_EDX_SPEC_CTRL": "spec-ctrl",
        "CPUID_7_0_EDX_SPEC_CTRL_SSBD": "ssbd",
        "CPUID_7_0_EDX_STIBP": "stibp",
        "CPUID_7_0_EDX_TSX_LDTRK": "tsx-ldtrk",
        "CPUID_7_1_EAX_AMX_FP16": "amx-fp16",
        "CPUID_7_1_EAX_AVX512_BF16": "avx512-bf16",
        "CPUID_7_1_EAX_AVX_IFMA": "avx-ifma",
        "CPUID_7_1_EAX_AVX_VNNI": "avx-vnni",
        "CPUID_7_1_EAX_CMPCCXADD": "cmpccxadd",
        "CPUID_7_1_EAX_FSRC": "fsrc",
        "CPUID_7_1_EAX_FSRS": "fsrs",
        "CPUID_7_1_EAX_FZRM": "fzrm",
        "CPUID_7_1_EDX_AVX_NE_CONVERT": "avx-ne-convert",
        "CPUID_7_1_EDX_AVX_VNNI_INT8": "avx-vnni-int8",
        "CPUID_7_1_EDX_PREFETCHITI": "prefetchiti",
        "CPUID_7_2_EDX_MCDT_NO": "mcdt-no",
        "CPUID_8000_0008_EBX_AMD_PSFD": "amd-psfd",
        "CPUID_8000_0008_EBX_AMD_SSBD": "amd-ssbd",
        "CPUID_8000_0008_EBX_CLZERO": "clzero",
        "CPUID_8000_0008_EBX_IBPB": "ibpb",
        "CPUID_8000_0008_EBX_IBRS": "ibrs",
        "CPUID_8000_0008_EBX_STIBP": "amd-stibp",
        "CPUID_8000_0008_EBX_STIBP_ALWAYS_ON": "stibp-always-on",
        "CPUID_8000_0008_EBX_WBNOINVD": "wbnoinvd",
        "CPUID_8000_0008_EBX_XSAVEERPTR": "xsaveerptr",
        "CPUID_8000_0021_EAX_AUTO_IBRS": "auto-ibrs",
        "CPUID_8000_0021_EAX_LFENCE_ALWAYS_SERIALIZING":
            "lfence-always-serializing",
        "CPUID_8000_0021_EAX_NULL_SEL_CLR_BASE": "null-sel-clr-base",
        "CPUID_8000_0021_EAX_No_NESTED_DATA_BP": "no-nested-data-bp",
        "CPUID_ACPI": "acpi",
        "CPUID_APIC": "apic",
        "CPUID_CLFLUSH": "clflush",
        "CPUID_CMOV": "cmov",
        "CPUID_CX8": "cx8",
        "CPUID_DE": "de",
        "CPUID_D_1_EAX_XFD": "xfd",
        "CPUID_EXT2_3DNOW": "3dnow",
        "CPUID_EXT2_3DNOWEXT": "3dnowext",
        "CPUID_EXT2_FFXSR": "fxsr_opt",
        "CPUID_EXT2_LM": "lm",
        "CPUID_EXT2_MMXEXT": "mmxext",
        "CPUID_EXT2_NX": "nx",
        "CPUID_EXT2_PDPE1GB": "pdpe1gb",
        "CPUID_EXT2_RDTSCP": "rdtscp",
        "CPUID_EXT2_SYSCALL": "syscall",
        "CPUID_EXT3_3DNOWPREFETCH": "3dnowprefetch",
        "CPUID_EXT3_ABM": "abm",
        "CPUID_EXT3_CR8LEG": "cr8legacy",
        "CPUID_EXT3_FMA4": "fma4",
        "CPUID_EXT3_LAHF_LM": "lahf_lm",
        "CPUID_EXT3_MISALIGNSSE": "misalignsse",
        "CPUID_EXT3_OSVW": "osvw",
        "CPUID_EXT3_PERFCORE": "perfctr_core",
        "CPUID_EXT3_SSE4A": "sse4a",
        "CPUID_EXT3_SVM": "svm",
        "CPUID_EXT3_TBM": "tbm",
        "CPUID_EXT3_XOP": "xop",
        "CPUID_EXT_AES": "aes",
        "CPUID_EXT_AVX": "avx",
        "CPUID_EXT_CX16": "cx16",
        "CPUID_EXT_F16C": "f16c",
        "CPUID_EXT_FMA": "fma",
        "CPUID_EXT_MOVBE": "movbe",
        "CPUID_EXT_PCID": "pcid",
        "CPUID_EXT_PCLMULQDQ": "pclmuldq",
        "CPUID_EXT_POPCNT": "popcnt",
        "CPUID_EXT_RDRAND": "rdrand",
        "CPUID_EXT_SSE3": "pni",
        "CPUID_EXT_SSE41": "sse4.1",
        "CPUID_EXT_SSE42": "sse4.2",
        "CPUID_EXT_SSSE3": "ssse3",
        "CPUID_EXT_TSC_DEADLINE_TIMER": "tsc-deadline",
        "CPUID_EXT_X2APIC": "x2apic",
        "CPUID_EXT_XSAVE": "xsave",
        "CPUID_FP87": "fpu",
        "CPUID_FXSR": "fxsr",
        "CPUID_MCA": "mca",
        "CPUID_MCE": "mce",
        "CPUID_MMX": "mmx",
        "CPUID_MSR": "msr",
        "CPUID_MTRR": "mtrr",
        "CPUID_PAE": "pae",
        "CPUID_PAT": "pat",
        "CPUID_PGE": "pge",
        "CPUID_PSE": "pse",
        "CPUID_PSE36": "pse36",
        "CPUID_SEP": "sep",
        "CPUID_SS": "ss",
        "CPUID_SSE": "sse",
        "CPUID_SSE2": "sse2",
        "CPUID_SVM_NPT": "npt",
        "CPUID_SVM_NRIPSAVE": "nrip-save",
        "CPUID_SVM_SVME_ADDR_CHK": "svme-addr-chk",
        "CPUID_SVM_VNMI": "vnmi",
        "CPUID_TSC": "tsc",
        "CPUID_VME": "vme",
        "CPUID_XSAVE_XGETBV1": "xgetbv1",
        "CPUID_XSAVE_XSAVEC": "xsavec",
        "CPUID_XSAVE_XSAVEOPT": "xsaveopt",
        "CPUID_XSAVE_XSAVES": "xsaves",
        "MSR_ARCH_CAP_FBSDP_NO": "fbsdp-no",
        "MSR_ARCH_CAP_IBRS_ALL": "ibrs-all",
        "MSR_ARCH_CAP_MDS_NO": "mds-no",
        "MSR_ARCH_CAP_PBRSB_NO": "pbrsb-no",
        "MSR_ARCH_CAP_PSCHANGE_MC_NO": "pschange-mc-no",
        "MSR_ARCH_CAP_PSDP_NO": "psdp-no",
        "MSR_ARCH_CAP_RDCL_NO": "rdctl-no",
        "MSR_ARCH_CAP_SBDR_SSDP_NO": "sbdr-ssdp-no",
        "MSR_ARCH_CAP_SKIP_L1DFL_VMENTRY": "skip-l1dfl-vmentry",
        "MSR_ARCH_CAP_TAA_NO": "taa-no",
        "MSR_CORE_CAP_SPLIT_LOCK_DETECT": "split-lock-detect",

        # FEAT_VMX_PROCBASED_CTLS
        "VMX_CPU_BASED_VIRTUAL_INTR_PENDING": "vmx-vintr-pending",
        "VMX_CPU_BASED_USE_TSC_OFFSETING": "vmx-tsc-offset",
        "VMX_CPU_BASED_HLT_EXITING": "vmx-hlt-exit",
        "VMX_CPU_BASED_INVLPG_EXITING": "vmx-invlpg-exit",
        "VMX_CPU_BASED_MWAIT_EXITING": "vmx-mwait-exit",
        "VMX_CPU_BASED_RDPMC_EXITING": "vmx-rdpmc-exit",
        "VMX_CPU_BASED_RDTSC_EXITING": "vmx-rdtsc-exit",
        "VMX_CPU_BASED_CR3_LOAD_EXITING": "vmx-cr3-load-noexit",
        "VMX_CPU_BASED_CR3_STORE_EXITING": "vmx-cr3-store-noexit",
        "VMX_CPU_BASED_CR8_LOAD_EXITING": "vmx-cr8-load-exit",
        "VMX_CPU_BASED_CR8_STORE_EXITING": "vmx-cr8-store-exit",
        "VMX_CPU_BASED_TPR_SHADOW": "vmx-flexpriority",
        "VMX_CPU_BASED_VIRTUAL_NMI_PENDING": "vmx-vnmi-pending",
        "VMX_CPU_BASED_MOV_DR_EXITING": "vmx-movdr-exit",
        "VMX_CPU_BASED_UNCOND_IO_EXITING": "vmx-io-exit",
        "VMX_CPU_BASED_USE_IO_BITMAPS": "vmx-io-bitmap",
        "VMX_CPU_BASED_MONITOR_TRAP_FLAG": "vmx-mtf",
        "VMX_CPU_BASED_USE_MSR_BITMAPS": "vmx-msr-bitmap",
        "VMX_CPU_BASED_MONITOR_EXITING": "vmx-monitor-exit",
        "VMX_CPU_BASED_PAUSE_EXITING": "vmx-pause-exit",
        "VMX_CPU_BASED_ACTIVATE_SECONDARY_CONTROLS": "vmx-secondary-ctls",

        # FEAT_VMX_SECONDARY_CTLS
        "VMX_SECONDARY_EXEC_VIRTUALIZE_APIC_ACCESSES": "vmx-apicv-xapic",
        "VMX_SECONDARY_EXEC_ENABLE_EPT": "vmx-ept",
        "VMX_SECONDARY_EXEC_DESC": "vmx-desc-exit",
        "VMX_SECONDARY_EXEC_RDTSCP": "vmx-rdtscp-exit",
        "VMX_SECONDARY_EXEC_VIRTUALIZE_X2APIC_MODE": "vmx-apicv-x2apic",
        "VMX_SECONDARY_EXEC_ENABLE_VPID": "vmx-vpid",
        "VMX_SECONDARY_EXEC_WBINVD_EXITING": "vmx-wbinvd-exit",
        "VMX_SECONDARY_EXEC_UNRESTRICTED_GUEST": "vmx-unrestricted-guest",
        "VMX_SECONDARY_EXEC_APIC_REGISTER_VIRT": "vmx-apicv-register",
        "VMX_SECONDARY_EXEC_VIRTUAL_INTR_DELIVERY": "vmx-apicv-vid",
        "VMX_SECONDARY_EXEC_PAUSE_LOOP_EXITING": "vmx-ple",
        "VMX_SECONDARY_EXEC_RDRAND_EXITING": "vmx-rdrand-exit",
        "VMX_SECONDARY_EXEC_ENABLE_INVPCID": "vmx-invpcid-exit",
        "VMX_SECONDARY_EXEC_ENABLE_VMFUNC": "vmx-vmfunc",
        "VMX_SECONDARY_EXEC_SHADOW_VMCS": "vmx-shadow-vmcs",
        "VMX_SECONDARY_EXEC_ENCLS_EXITING": "vmx-encls-exit",
        "VMX_SECONDARY_EXEC_RDSEED_EXITING": "vmx-rdseed-exit",
        "VMX_SECONDARY_EXEC_ENABLE_PML": "vmx-pml",
        "VMX_SECONDARY_EXEC_XSAVES": "vmx-xsaves",
        "VMX_SECONDARY_EXEC_TSC_SCALING": "vmx-tsc-scaling",
        "VMX_SECONDARY_EXEC_ENABLE_USER_WAIT_PAUSE": "vmx-enable-user-wait-pause",

        # FEAT_VMX_PINBASED_CTLS
        "VMX_PIN_BASED_EXT_INTR_MASK": "vmx-intr-exit",
        "VMX_PIN_BASED_NMI_EXITING": "vmx-nmi-exit",
        "VMX_PIN_BASED_VIRTUAL_NMIS": "vmx-vnmi",
        "VMX_PIN_BASED_VMX_PREEMPTION_TIMER": "vmx-preemption-timer",
        "VMX_PIN_BASED_POSTED_INTR": "vmx-posted-intr",

        # FEAT_VMX_EXIT_CTLS
        "VMX_VM_EXIT_SAVE_DEBUG_CONTROLS": "vmx-exit-nosave-debugctl",
        "VMX_VM_EXIT_LOAD_IA32_PERF_GLOBAL_CTRL": "vmx-exit-load-perf-global-ctrl",
        "VMX_VM_EXIT_ACK_INTR_ON_EXIT": "vmx-exit-ack-intr",
        "VMX_VM_EXIT_SAVE_IA32_PAT": "vmx-exit-save-pat",
        "VMX_VM_EXIT_LOAD_IA32_PAT": "vmx-exit-load-pat",
        "VMX_VM_EXIT_SAVE_IA32_EFER": "vmx-exit-save-efer",
        "VMX_VM_EXIT_LOAD_IA32_EFER": "vmx-exit-load-efer",
        "VMX_VM_EXIT_SAVE_VMX_PREEMPTION_TIMER": "vmx-exit-save-preemption-timer",
        "VMX_VM_EXIT_CLEAR_BNDCFGS": "vmx-exit-clear-bndcfgs",
        "VMX_VM_EXIT_CLEAR_IA32_RTIT_CTL": "vmx-exit-clear-rtit-ctl",
        "VMX_VM_EXIT_LOAD_IA32_PKRS": "vmx-exit-load-pkrs",

        # FEAT_VMX_ENTRY_CTLS
        "VMX_VM_ENTRY_LOAD_DEBUG_CONTROLS": "vmx-entry-noload-debugctl",
        "VMX_VM_ENTRY_IA32E_MODE": "vmx-entry-ia32e-mode",
        "VMX_VM_ENTRY_LOAD_IA32_PERF_GLOBAL_CTRL": "vmx-entry-load-perf-global-ctrl",
        "VMX_VM_ENTRY_LOAD_IA32_PAT": "vmx-entry-load-pat",
        "VMX_VM_ENTRY_LOAD_IA32_EFER": "vmx-entry-load-efer",
        "VMX_VM_ENTRY_LOAD_BNDCFGS": "vmx-entry-load-bndcfgs",
        "VMX_VM_ENTRY_LOAD_IA32_RTIT_CTL": "vmx-entry-load-rtit-ctl",
        "VMX_VM_ENTRY_LOAD_IA32_PKRS": "vmx-entry-load-pkrs",

        # FEAT_VMX_MISC
        "MSR_VMX_MISC_STORE_LMA": "vmx-store-lma",
        "MSR_VMX_MISC_ACTIVITY_HLT": "vmx-activity-hlt",
        "MSR_VMX_MISC_ACTIVITY_SHUTDOWN": "vmx-activity-shutdown",
        "MSR_VMX_MISC_ACTIVITY_WAIT_SIPI": "vmx-activity-wait-sipi",
        "MSR_VMX_MISC_VMWRITE_VMEXIT": "vmx-vmwrite-vmexit-fields",
        "MSR_VMX_MISC_ZERO_LEN_INJECT": "vmx-zero-len-inject",

        # FEAT_VMX_EPT_VPID_CAPS
        "MSR_VMX_EPT_EXECONLY": "vmx-ept-execonly",
        "MSR_VMX_EPT_PAGE_WALK_LENGTH_4": "vmx-page-walk-4",
        "MSR_VMX_EPT_PAGE_WALK_LENGTH_5": "vmx-page-walk-5",
        "MSR_VMX_EPT_2MB": "vmx-ept-2mb",
        "MSR_VMX_EPT_1GB": "vmx-ept-1gb",
        "MSR_VMX_EPT_INVEPT": "vmx-invept",
        "MSR_VMX_EPT_AD_BITS": "vmx-eptad",
        "MSR_VMX_EPT_ADVANCED_VMEXIT_INFO": "vmx-ept-advanced-exitinfo",
        "MSR_VMX_EPT_INVEPT_SINGLE_CONTEXT": "vmx-invept-single-context",
        "MSR_VMX_EPT_INVEPT_ALL_CONTEXT": "vmx-invept-all-context",
        "MSR_VMX_EPT_INVVPID": "vmx-invvpid",
        "MSR_VMX_EPT_INVVPID_SINGLE_ADDR": "vmx-invvpid-single-addr",
        "MSR_VMX_EPT_INVVPID_ALL_CONTEXT": "vmx-invvpid-all-context",
        "MSR_VMX_EPT_INVVPID_SINGLE_CONTEXT_NOGLOBALS": "vmx-invvpid-single-context-noglobals",

        # FEAT_VMX_BASIC
        "MSR_VMX_BASIC_INS_OUTS": "vmx-ins-outs",
        "MSR_VMX_BASIC_TRUE_CTLS": "vmx-true-ctls",
        "MSR_VMX_BASIC_ANY_ERRCODE": "vmx-any-errcode",

        # FEAT_VMX_VMFUNC
        "MSR_VMX_VMFUNC_EPT_SWITCHING": "vmx-eptp-switching",
    }

    ignore = any([
        name in ("0", "model", "model-id", "stepping"),
        name in ("CPUID_EXT_MONITOR", "monitor"),
        name in ("MSR_VMX_BASIC_DUAL_MONITOR", "dual-monitor"),
        name in ("CPUID_EXT3_TOPOEXT", "topoext"),
        name in ("MSR_VMX_EPT_UC", "MSR_VMX_EPT_WB"),
        name in ("MSR_VMX_EPT_INVVPID_SINGLE_CONTEXT"),
    ])

    if ignore:
        return None

    if name in T:
        return T[name]

    for v in T.values():
        if name.replace("-", "_") == v.replace("-", "_"):
            return v

    print(f"warning: Unknown feature '{name}'")
    return name


def readline_cont(f):
    """Read one logical line from a file `f` i.e. continues lines that end in
    a backslash."""

    line = f.readline()
    while line.endswith("\\\n"):
        line = line[:-2] + " " + f.readline()
    return line


def read_builtin_x86_defs(filename):
    """Extract content between begin_mark and end_mark from file `filename` as
    string, while expanding shorthand macros like "I486_FEATURES"."""

    begin_mark = re.compile(
        "^static( const)? X86CPUDefinition builtin_x86_defs\\[\\] = {$")
    end_mark = "};\n"
    shorthand = re.compile("^#define ([A-Z0-9_]+_FEATURES) (.*)$")
    lines = list()
    shorthands = dict()

    with open(filename, "rt") as f:
        while True:
            line = readline_cont(f)
            if not line:
                raise RuntimeError("begin mark not found")
            match = begin_mark.match(line)
            if match:
                break
            match = shorthand.match(line)
            if match:
                # TCG definitions are irrelevant for cpu models
                newk = match.group(1)
                if newk.startswith("TCG_"):
                    continue

                # remove comments, whitespace and bit operators, effectively
                # turning the bitfield into a list
                newv = re.sub("([()|\t\n])|(/\\*.*?\\*/)", " ", match.group(2))

                # resolve recursive shorthands
                for k, v in shorthands.items():
                    newv = newv.replace(k, v)

                shorthands[newk] = newv

        while True:
            line = readline_cont(f)
            if line == end_mark:
                break
            if not line:
                raise RuntimeError("end marker not found")

            # apply shorthands
            for k, v in shorthands.items():
                line = line.replace(k, v)
            lines.append(line)

    return "".join(lines)


def transform(item):
    """Recursively transform a Lark syntax tree into python native objects."""

    if isinstance(item, lark.lexer.Token):
        return str(item)

    if item.data == "list":
        retval = list()
        for child in item.children:
            value = transform(child)
            if value is None:
                continue
            retval.append(value)
        return retval

    if item.data == "map":
        retval = dict()
        for child in item.children:
            if len(child.children) != 2:
                raise RuntimeError("map entry with more than 2 elements")
            key = transform(child.children[0])
            value = transform(child.children[1])
            if key is None:
                raise RuntimeError("map entry with 'None' key")
            if value is None:
                continue
            retval[key] = value
        return retval

    if item.data == "text":
        retval = list()
        for child in item.children:
            value = transform(child)
            if value is None:
                continue
            retval.append(value)
        return " ".join(retval)

    if item.data == "value":
        if item.children:
            raise RuntimeError("empty list is not empty")
        return None

    raise RuntimeError("unexpected item type")


def get_signature(outdir, model):
    file = os.path.join(outdir, f"x86_{model}.xml")

    if not os.path.isfile(file):
        return None

    xml = lxml.etree.parse(file)

    signature = []
    for sig in xml.xpath("//signature"):
        attr = sig.attrib
        family = attr["family"]
        model = attr["model"]
        if "stepping" in attr:
            stepping = attr["stepping"]
        else:
            stepping = None

        signature.append((family, model, stepping))

    return signature


def expand_model(outdir, model):
    """Expand a qemu cpu model description that has its feature split up into
    different fields and may have differing versions into several libvirt-
    friendly cpu models."""

    result = {
        "name": model.pop(".name"),
        "vendor": translate_vendor(model.pop(".vendor")),
        "features": set(),
        "extra": dict(),
        "signature": list(),
    }

    if ".family" in model and ".model" in model:
        result["signature"].append((model.pop(".family"),
                                    model.pop(".model"),
                                    None))

    for k in [k for k in model if k.startswith(".features")]:
        v = model.pop(k)
        for feature in v.split():
            translated = translate_feature(feature)
            if translated:
                result["features"].add(translated)

    versions = model.pop(".versions", [])
    for k, v in model.items():
        result["extra"]["model" + k] = v

    print(result['name'])
    yield result

    name = result["name"]
    for version in versions:
        result = copy.deepcopy(result)

        ver = int(version.pop(".version"))
        result["name"] = f"{name}-v{ver}"
        result["base"] = name

        alias = version.pop(".alias", None)
        if not alias and ver == 1:
            alias = name

            sig = get_signature(outdir, name)
            if sig:
                result["signature"] = sig

        props = version.pop(".props", dict())
        for k, v in props:
            if k not in ("model-id", "stepping", "model"):
                k = translate_feature(k)
            if k is None:
                continue

            if v == "on":
                result["features"].add(k)
            elif v == "off" and k in result["features"]:
                result["features"].remove(k)
            else:
                result["extra"]["property." + k] = v

        for k, v in version.items():
            result["extra"]["version" + k] = v

        if alias:
            print(f"v{ver}: {result['name']} => {alias}")
            yield {
                "vendor": result["vendor"],
                "name": result["name"],
                "base": result["base"],
                "alias": alias,
                "extra": None,
                "features": [],
            }

            if ver != 1:
                result["name"] = alias
                print(f"v{ver}: {result['name']}")
                yield result
        else:
            print(f"v{ver}: {result['name']}")
            yield result


def output_model(f, extra, model):
    if model["extra"]:
        with open(extra, "wt") as ex:
            ex.write("# THIS FILE SHOULD NEVER BE ADDED TO A COMMIT\n")
            ex.write("extra info from qemu:\n")
            for k, v in model["extra"].items():
                ex.write(f"  {k}: {v}\n")

    decode = "off" if "base" in model else "on"

    f.write("<cpus>\n")
    f.write(f"  <model name='{model['name']}'>\n")
    f.write(f"    <decode host='on' guest='{decode}'/>\n")

    if "alias" in model:
        f.write(f"    <model name='{model['alias']}'/>\n")
    else:
        for sig_family, sig_model, sig_stepping in model['signature']:
            f.write(f"    <signature family='{sig_family}' model='{sig_model}'")
            if sig_stepping:
                f.write(f" stepping='{sig_stepping}'")
            f.write("/>\n")
        f.write(f"    <vendor name='{model['vendor']}'/>\n")

    for feature in sorted(model["features"]):
        f.write(f"    <feature name='{feature}'/>\n")
    f.write("  </model>\n")
    f.write("</cpus>\n")


def update_index(outdir, models):
    index = os.path.join(outdir, "index.xml")
    xml = lxml.etree.parse(index)

    for vendor, files in models.items():
        groups = xml.xpath(f"//arch[@name='x86']/group[@name='{vendor} CPU models']")
        if not groups:
            continue

        group = groups[-1]
        last = group.getchildren()[-1]
        group_indent = last.tail
        indent = f"{group_indent}  "
        last.tail = indent

        for file in files:
            include = lxml.etree.SubElement(group, "include", filename=file)
            include.tail = indent

        group.getchildren()[-1].tail = group_indent

    out = lxml.etree.tostring(xml, encoding="UTF-8")
    out = out.decode("UTF-8").replace('"', "'")

    with open(index, "w") as f:
        f.write(out)
        f.write("\n")


def main():
    parser = argparse.ArgumentParser(
        description="Synchronize x86 cpu models from QEMU i386 target.")
    parser.add_argument(
        "qemu",
        help="Path to QEMU source code",
        type=os.path.realpath)
    parser.add_argument(
        "outdir",
        help="Path to 'src/cpu_map' directory in the libvirt repository",
        type=os.path.realpath)

    args = parser.parse_args()

    cpufile = os.path.join(args.qemu, 'target/i386/cpu.c')
    if not os.path.isfile(cpufile):
        parser.print_help()
        exit("QEMU source directory not found")

    builtin_x86_defs = read_builtin_x86_defs(cpufile)

    ast = lark.Lark(r"""
        list: value ( "," value )* ","?
        map: keyvalue ( "," keyvalue )* ","?
        keyvalue: IDENTIFIER "=" value
        ?value: text | "{" "}" | "{" list "}" | "{" map "}"
        text: (IDENTIFIER | "\"" (/[^"]+/)? "\"")+
        IDENTIFIER: /[\[\]\._&a-zA-Z0-9]/+
        %ignore (" " | "\r" | "\n" | "\t" | "|" )+
        %ignore "(" ( "X86CPUVersionDefinition" | "PropValue" ) "[])"
        %ignore "//" /.*?/ "\n"
        %ignore "/*" /(.|\n)*?/ "*/"
        """, start="list").parse(builtin_x86_defs)

    models_json = transform(ast)

    models = list()
    for model in models_json:
        models.extend(expand_model(args.outdir, model))

    files = dict()

    for model in models:
        name = f"x86_{model['name']}.xml"
        path = os.path.join(args.outdir, name)

        if os.path.isfile(path):
            # Ignore existing models as CPU models in libvirt should never
            # change once released.
            continue

        vendor = model['vendor']
        if vendor:
            if vendor not in files:
                files[vendor] = []
            files[vendor].append(name)

        extra = os.path.join(args.outdir, f"x86_{model['name']}.extra")
        with open(path, "wt") as f:
            output_model(f, extra, model)

    update_index(args.outdir, files)

    features = set()
    for model in models:
        features.update(model["features"])

    try:
        filename = os.path.join(args.outdir, "x86_features.xml")
        dom = lxml.etree.parse(filename)
        known = [x.attrib["name"] for x in dom.getroot().iter("feature")]
        unknown = [x for x in features if x not in known and x is not None]
    except Exception as e:
        unknown = []
        print(f"warning: Unable to read libvirt x86_features.xml: {e}")

    for x in unknown:
        print(f"warning: Feature unknown to libvirt: {x}")


if __name__ == "__main__":
    main()
