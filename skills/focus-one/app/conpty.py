"""Minimal Windows pseudo console (ConPTY) wrapper using ctypes only.

Runs a command inside a pseudo console so its screen can be streamed to a browser terminal (xterm.js)
instead of a separate console window. Needs Windows 10 1809 or later.
"""
import ctypes
import msvcrt
import os
import subprocess
from ctypes import wintypes as W

_k32 = ctypes.WinDLL("kernel32", use_last_error=True)

EXTENDED_STARTUPINFO_PRESENT = 0x00080000
CREATE_UNICODE_ENVIRONMENT = 0x00000400
STARTF_USESTDHANDLES = 0x00000100
PROC_THREAD_ATTRIBUTE_PSEUDOCONSOLE = 0x00020016
INFINITE = 0xFFFFFFFF
STILL_ACTIVE = 259


class COORD(ctypes.Structure):
    _fields_ = [("X", W.SHORT), ("Y", W.SHORT)]


class STARTUPINFOW(ctypes.Structure):
    _fields_ = [("cb", W.DWORD), ("lpReserved", W.LPWSTR), ("lpDesktop", W.LPWSTR), ("lpTitle", W.LPWSTR),
                ("dwX", W.DWORD), ("dwY", W.DWORD), ("dwXSize", W.DWORD), ("dwYSize", W.DWORD),
                ("dwXCountChars", W.DWORD), ("dwYCountChars", W.DWORD), ("dwFillAttribute", W.DWORD),
                ("dwFlags", W.DWORD), ("wShowWindow", W.WORD), ("cbReserved2", W.WORD),
                ("lpReserved2", ctypes.c_void_p), ("hStdInput", W.HANDLE), ("hStdOutput", W.HANDLE),
                ("hStdError", W.HANDLE)]


class STARTUPINFOEXW(ctypes.Structure):
    _fields_ = [("StartupInfo", STARTUPINFOW), ("lpAttributeList", ctypes.c_void_p)]


class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [("hProcess", W.HANDLE), ("hThread", W.HANDLE), ("dwProcessId", W.DWORD), ("dwThreadId", W.DWORD)]


def _sig(name, res, *args):
    fn = getattr(_k32, name)
    fn.restype, fn.argtypes = res, list(args)
    return fn


try:
    _CreatePseudoConsole = _sig("CreatePseudoConsole", ctypes.c_long, COORD, W.HANDLE, W.HANDLE, W.DWORD,
                                ctypes.POINTER(W.HANDLE))
    _ResizePseudoConsole = _sig("ResizePseudoConsole", ctypes.c_long, W.HANDLE, COORD)
    _ClosePseudoConsole = _sig("ClosePseudoConsole", None, W.HANDLE)
    AVAILABLE = True
except AttributeError:  # Windows older than 10 1809
    AVAILABLE = False
_CreatePipe = _sig("CreatePipe", W.BOOL, ctypes.POINTER(W.HANDLE), ctypes.POINTER(W.HANDLE), ctypes.c_void_p, W.DWORD)
_InitAttrList = _sig("InitializeProcThreadAttributeList", W.BOOL, ctypes.c_void_p, W.DWORD, W.DWORD,
                     ctypes.POINTER(ctypes.c_size_t))
_UpdateAttr = _sig("UpdateProcThreadAttribute", W.BOOL, ctypes.c_void_p, W.DWORD, ctypes.c_size_t, ctypes.c_void_p,
                   ctypes.c_size_t, ctypes.c_void_p, ctypes.c_void_p)
_DeleteAttrList = _sig("DeleteProcThreadAttributeList", None, ctypes.c_void_p)
_CreateProcessW = _sig("CreateProcessW", W.BOOL, W.LPCWSTR, W.LPWSTR, ctypes.c_void_p, ctypes.c_void_p, W.BOOL,
                       W.DWORD, ctypes.c_void_p, W.LPCWSTR, ctypes.POINTER(STARTUPINFOEXW),
                       ctypes.POINTER(PROCESS_INFORMATION))
_WaitForSingleObject = _sig("WaitForSingleObject", W.DWORD, W.HANDLE, W.DWORD)
_GetExitCodeProcess = _sig("GetExitCodeProcess", W.BOOL, W.HANDLE, ctypes.POINTER(W.DWORD))
_CloseHandle = _sig("CloseHandle", W.BOOL, W.HANDLE)


def _check(ok, what):
    if not ok:
        raise ctypes.WinError(ctypes.get_last_error(), what)


class ConPty:
    """A process attached to its own pseudo console. read()/write() carry UTF-8 VT text."""

    def __init__(self, args, cwd=None, cols=120, rows=30):
        if not AVAILABLE:
            raise OSError("ConPTY is not available on this Windows version")
        in_r, in_w, out_r, out_w = W.HANDLE(), W.HANDLE(), W.HANDLE(), W.HANDLE()
        _check(_CreatePipe(ctypes.byref(in_r), ctypes.byref(in_w), None, 0), "CreatePipe")
        _check(_CreatePipe(ctypes.byref(out_r), ctypes.byref(out_w), None, 0), "CreatePipe")
        self._hpc = W.HANDLE()
        hr = _CreatePseudoConsole(COORD(cols, rows), in_r, out_w, 0, ctypes.byref(self._hpc))
        # The pseudo console keeps its own copies of these ends.
        _CloseHandle(in_r)
        _CloseHandle(out_w)
        if hr != 0:
            _CloseHandle(in_w)
            _CloseHandle(out_r)
            raise OSError(f"CreatePseudoConsole failed (0x{hr & 0xFFFFFFFF:08X})")
        self._in = msvcrt.open_osfhandle(in_w.value, 0)
        self._out = msvcrt.open_osfhandle(out_r.value, os.O_RDONLY)

        size = ctypes.c_size_t()
        _InitAttrList(None, 1, 0, ctypes.byref(size))
        attrs = ctypes.create_string_buffer(size.value)
        si = STARTUPINFOEXW()
        si.StartupInfo.cb = ctypes.sizeof(STARTUPINFOEXW)
        # Without this the child inherits the server's redirected std handles (its log file)
        # instead of talking to the pseudo console.
        si.StartupInfo.dwFlags = STARTF_USESTDHANDLES
        si.lpAttributeList = ctypes.cast(attrs, ctypes.c_void_p)
        pi = PROCESS_INFORMATION()
        try:
            _check(_InitAttrList(si.lpAttributeList, 1, 0, ctypes.byref(size)), "InitializeProcThreadAttributeList")
            _check(_UpdateAttr(si.lpAttributeList, 0, PROC_THREAD_ATTRIBUTE_PSEUDOCONSOLE, self._hpc,
                               ctypes.sizeof(W.HANDLE), None, None), "UpdateProcThreadAttribute")
            cmdline = ctypes.create_unicode_buffer(subprocess.list2cmdline(args))
            _check(_CreateProcessW(None, cmdline, None, None, False,
                                   EXTENDED_STARTUPINFO_PRESENT | CREATE_UNICODE_ENVIRONMENT, None, cwd,
                                   ctypes.byref(si), ctypes.byref(pi)), "CreateProcessW")
        except OSError:
            self.close()
            raise
        finally:
            _DeleteAttrList(si.lpAttributeList)
        _CloseHandle(pi.hThread)
        self._proc = pi.hProcess
        self.pid = pi.dwProcessId

    def read(self, n=65536):
        """Blocking read of screen output. b"" once the pseudo console is closed."""
        try:
            return os.read(self._out, n)
        except OSError:
            return b""

    def write(self, data):
        if self._in is not None:
            os.write(self._in, data)

    def resize(self, cols, rows):
        if self._hpc:
            _ResizePseudoConsole(self._hpc, COORD(max(2, cols), max(2, rows)))

    def wait(self):
        """Block until the process exits; returns its exit code."""
        _WaitForSingleObject(self._proc, INFINITE)
        code = W.DWORD()
        _GetExitCodeProcess(self._proc, ctypes.byref(code))
        return code.value

    def kill(self):
        """End the process and everything it started (claude runs as its child)."""
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(self.pid)], capture_output=True,
                       creationflags=subprocess.CREATE_NO_WINDOW)

    def close(self):
        """Close the pseudo console; pending output is flushed and read() then returns b""."""
        hpc, self._hpc = self._hpc, None
        if hpc:
            _ClosePseudoConsole(hpc)
        fd, self._in = self._in, None  # never close an fd number twice; it may be reused by then
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass
        proc, self._proc = getattr(self, "_proc", None), None
        if proc:
            _CloseHandle(proc)

    def close_output(self):
        """Release the output pipe once read() has returned b""."""
        try:
            os.close(self._out)
        except OSError:
            pass
