# -*- coding: utf-8 -*-
from gph_pydbg_defines import *

kernel32 = windll.kernel32

class debugger():
    def __init__(self):
        self.h_process          = None
        self.pid                = None
        self.debugger_active    = False
        self.h_thread           = None
        self.context            = None
        self.breakpoints        = {}
        self.first_breakpoint   = True

        self.exception          = None
        self.exception_address  = None

    def load(self,path_to_exe):
        # dwCreation flag determines how to create the process
        # set creation_flags = CREATE_NEW_CONSOLE if you want
        # to see the calculator GUI
        creation_flags = DEBUG_PROCESS

        # instantiate the structs
        startupinfo = STARTUPINFO()
        process_information = PROCESS_INFORMATION()

        # The following two options allow the started process
        # to be shown as a separate window. This also illustrates
        # how different settings in the STARTUPINFO struct can affect
        # the debuggee.
        startupinfo.dwFlags     = 0x1
        startupinfo.wShowWindow = 0x0

        # We then initialize the cb variable in the STARTUPINFO struct
        # which is just the size of the struct itself
        startupinfo.cb = sizeof(startupinfo)

        if kernel32.CreateProcessA(path_to_exe,
                                    None,
                                    None,
                                    None,
                                    None,
                                    creation_flags,
                                    None,
                                    None,
                                    byref(startupinfo),
                                    byref(process_information)):
            print "[*] We have successfully launched the process!"
            print "[*] PID: %d" % process_information.dwProcessId

            # Obtain a valid handle to the newly created process
            # and store it for future access
            self.h_process = self.open_process(process_information.dwProcessId)
        else:
            print "[*] Error: 0x%08x." % kernel32.GetLastError()

    def open_process(self, pid):
        h_process = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
        return h_process

    def attach(self, pid):
        self.h_process = self.open_process(pid)

        # We attempt to attach to the process
        # if this fails we exit the call
        if kernel32.DebugActiveProcess(pid):
            self.debugger_active = True
            self.pid = int(pid)
            # self.run()  #这一句在3.1节里不能删掉，否则无法正常运行。
                          #3.2及后要注释掉，不然会卡在这里
        else:
            print "[*] Unable to attach to the process."

    def run(self):
        # Now we have to poll the debuggee for
        # debugging events
        while self.debugger_active == True:
            self.get_debug_event()

    def get_debug_event(self):
        debug_event     = DEBUG_EVENT()
        continue_status = DBG_CONTINUE

        if kernel32.WaitForDebugEvent(byref(debug_event), 100):
            # Let's obtain the thread and context information
            self.h_thread       = self.open_thread(debug_event.dwThreadId)
            self.context        = self.get_thread_context(self.h_thread)
            self.debug_event    = debug_event

            print "Event Code: %d Thread ID: %d" % (debug_event.dwDebugEventCode,
                                                    debug_event.dwThreadId)

            # If the event code is an exception, we want to
            # examine it further.
            if debug_event.dwDebugEventCode == EXCEPTION_DEBUG_EVENT:
                # Obtain the exception code
                exception = \
                    debug_event.u.Exception.ExceptionRecord.ExceptionCode
                self.exception_address = \
                    debug_event.u.Exception.ExceptionRecord.ExceptionAddress

                if exception == EXCEPTION_ACCESS_VIOLATION:
                    print "Access Violation Detected."
                    # If a breakpoint is detected, we call an internal
                    # handler.
                elif exception == EXCEPTION_BREAKPOINT:
                    continue_status = self.exception_handler_breakpoint()
                elif exception == EXCEPTION_GUARD_PAGE:
                    print "Guard Page Access Detected."
                elif exception == EXCEPTION_SINGLE_STEP:
                    print "Single Stepping."

            kernel32.ContinueDebugEvent(debug_event.dwProcessId,
                                        debug_event.dwThreadId,
                                        continue_status)

    def exception_handler_breakpoint(self):
        print "[*] Exception address: 0x%08x" % self.exception_address
        # check if the breakpoint is one that we set
        if not self.breakpoints.has_key(self.exception_address):

            # if it is the first Windows driven breakpoint
            # then let's just continue on
            if self.first_breakpoint:
                self.first_breakpoint = False
                print "[*] Hit the first breakpoint."
                return DBG_CONTINUE

        else:
            print "[*] Hit user defined breakpoint."
            # this is where we handle the breakpoints we set
            # first put the original byte back
            self.write_process_memory(self.exception_address, self.breakpoints[self.exception_address])

            # obtain a fresh context record, reset EIP back to the
            # original byte and then set the thread's context record
            # with the new EIP value
            self.context = self.get_thread_context(h_thread=self.h_thread)
            self.context.Rip -= 1

            kernel32.SetThreadContext(self.h_thread, byref(self.context))

        return DBG_CONTINUE

    def detach(self):
        if kernel32.DebugActiveProcessStop(self.pid):
            print "[*] Finished debugging. Exiting..."
            return True
        else:
            print "There was an error"
            return False

    def open_thread(self, thread_id):
        h_thread = kernel32.OpenThread(THREAD_ALL_ACCESS, None, thread_id)

        if h_thread is not None:
            return h_thread
        else:
            print "[*] Could not obtain a valid thread handle."
            return False

    def enumerate_threads(self):
        thread_entry = THREADENTRY32()
        thread_list = []
        snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, self.pid)

        if snapshot is not None:
            # You have to set the size of the struct
            # or the call will fail
            thread_entry.dwSize = sizeof(thread_entry)
            success = kernel32.Thread32First(snapshot, byref(thread_entry))

            while success:
                if thread_entry.th32OwnerProcessID == self.pid:
                    thread_list.append(thread_entry.th32ThreadID)
                success = kernel32.Thread32Next(snapshot, byref(thread_entry))
            kernel32.CloseHandle(snapshot)  # 此处要调整语句缩进
            return thread_list
        else:
            return False

    def get_thread_context(self, thread_id=None, h_thread=None):
        context64 = WOW64_CONTEXT()
        context64.ContextFlags = CONTEXT_FULL | CONTEXT_DEBUG_REGISTERS

        # Obtain a handle to the thread
        if h_thread is None:
            h_thread = self.open_thread(thread_id)
        if kernel32.GetThreadContext(h_thread, byref(context64)):
            kernel32.CloseHandle(h_thread)
            return context64
        else:
            return False

    def read_process_memory(self,address,length):
        data        = ""
        read_buf    = create_string_buffer(length)
        count       = c_ulong(0)

        if not kernel32.ReadProcessMemory(self.h_process,
                                          c_longlong(address),
                                          read_buf,
                                          length,
                                          byref(count)):
            return False
        else:
            data += read_buf.raw
            return data

    def write_process_memory(self,address,data):
        count   = c_ulong(0)
        length  = len(data)
        c_data  = c_char_p(data[count.value:])

        if not kernel32.WriteProcessMemory(self.h_process,
                                           c_longlong(address),
                                           c_data,
                                           length,
                                           byref(count)):
            return False
        else:
            return True

    def bp_set(self,address):
        if not self.breakpoints.has_key(address):
            try:
                original_byte = self.read_process_memory(address, 1)

                self.write_process_memory(address, "\xCC")

                self.breakpoints[address] = original_byte
            except:
                return False
            return True

    def func_resolve(self,dll,function):
        # 不指定返回值，python会将返回值默认当做int处理，导致溢出
        kernel32.GetModuleHandleA.restype = c_ulonglong
        kernel32.GetProcAddress.restype = c_longlong

        handle  = c_longlong(kernel32.GetModuleHandleA(dll))
        # 此时handle的实际类型为long，需要再次转换成 longlong，否则会报错 long int too long to convert
        address = kernel32.GetProcAddress(handle, function)

        kernel32.CloseHandle(handle)
        return address



