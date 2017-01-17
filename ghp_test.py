# -*- coding: utf-8 -*-
import ghp_pydbg

debugger = ghp_pydbg.debugger()
pid = raw_input("Enter the PID of the process to attach to: ")

debugger.attach(int(pid))
debugger.run()
debugger.detach()
