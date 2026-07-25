from __future__ import annotations

import ctypes
import os
from ctypes import wintypes
from pathlib import Path


user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)

kernel32.GetModuleHandleW.restype = wintypes.HINSTANCE
user32.CreateWindowExW.argtypes = [
    wintypes.DWORD,
    wintypes.LPCWSTR,
    wintypes.LPCWSTR,
    wintypes.DWORD,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    wintypes.HWND,
    wintypes.HMENU,
    wintypes.HINSTANCE,
    ctypes.c_void_p,
]
user32.CreateWindowExW.restype = wintypes.HWND
user32.DefWindowProcW.argtypes = [
    wintypes.HWND,
    wintypes.UINT,
    wintypes.WPARAM,
    wintypes.LPARAM,
]
user32.DefWindowProcW.restype = ctypes.c_ssize_t
user32.SendMessageW.argtypes = [
    wintypes.HWND,
    wintypes.UINT,
    wintypes.WPARAM,
    wintypes.LPARAM,
]
user32.SendMessageW.restype = ctypes.c_ssize_t
user32.SetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPCWSTR]
user32.EnableWindow.argtypes = [wintypes.HWND, wintypes.BOOL]
user32.DestroyWindow.argtypes = [wintypes.HWND]
user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
user32.UpdateWindow.argtypes = [wintypes.HWND]
user32.MessageBoxW.argtypes = [
    wintypes.HWND,
    wintypes.LPCWSTR,
    wintypes.LPCWSTR,
    wintypes.UINT,
]
user32.LoadCursorW.restype = wintypes.HANDLE
gdi32.GetStockObject.restype = wintypes.HANDLE

WM_DESTROY = 0x0002
WM_CLOSE = 0x0010
WM_COMMAND = 0x0111
WM_SETFONT = 0x0030
WS_OVERLAPPED = 0x00000000
WS_CAPTION = 0x00C00000
WS_SYSMENU = 0x00080000
WS_VISIBLE = 0x10000000
WS_CHILD = 0x40000000
BS_PUSHBUTTON = 0x00000000
SS_LEFT = 0x00000000
WS_EX_TOPMOST = 0x00000008
SW_SHOW = 5
DEFAULT_GUI_FONT = 17

START_ID = 1001
STOP_ID = 1002
OPEN_ID = 1003
CLOSE_ID = 1004

WNDPROC = ctypes.WINFUNCTYPE(
    ctypes.c_ssize_t,
    wintypes.HWND,
    wintypes.UINT,
    wintypes.WPARAM,
    wintypes.LPARAM,
)


class WNDCLASSW(ctypes.Structure):
    _fields_ = [
        ("style", wintypes.UINT),
        ("lpfnWndProc", WNDPROC),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", wintypes.HINSTANCE),
        ("hIcon", wintypes.HICON),
        ("hCursor", wintypes.HANDLE),
        ("hbrBackground", wintypes.HBRUSH),
        ("lpszMenuName", wintypes.LPCWSTR),
        ("lpszClassName", wintypes.LPCWSTR),
    ]


class Overlay:
    def __init__(self, on_start, on_stop, on_quit):
        self._on_start = on_start
        self._on_stop = on_stop
        self._on_quit = on_quit
        self._last_output: Path | None = None
        self._closing = False
        self._class_name = "SkillRecorderWindow"
        self._wndproc_ref = WNDPROC(self._wndproc)
        self._instance = kernel32.GetModuleHandleW(None)
        self._register_window_class()
        self._hwnd = self._create_main_window()
        self._font = gdi32.GetStockObject(DEFAULT_GUI_FONT)
        self._create_controls()

    def _register_window_class(self) -> None:
        window_class = WNDCLASSW()
        window_class.lpfnWndProc = self._wndproc_ref
        window_class.hInstance = self._instance
        window_class.hCursor = user32.LoadCursorW(None, 32512)
        window_class.hbrBackground = wintypes.HBRUSH(6)
        window_class.lpszClassName = self._class_name
        atom = user32.RegisterClassW(ctypes.byref(window_class))
        if not atom and ctypes.get_last_error() != 1410:
            raise ctypes.WinError()

    def _create_main_window(self) -> int:
        hwnd = user32.CreateWindowExW(
            WS_EX_TOPMOST,
            self._class_name,
            "Skill Recorder for Windows",
            WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU,
            40,
            40,
            470,
            230,
            None,
            None,
            self._instance,
            None,
        )
        if not hwnd:
            raise ctypes.WinError()
        return hwnd

    def _control(
        self,
        class_name: str,
        text: str,
        style: int,
        x: int,
        y: int,
        width: int,
        height: int,
        control_id: int,
    ) -> int:
        hwnd = user32.CreateWindowExW(
            0,
            class_name,
            text,
            WS_VISIBLE | WS_CHILD | style,
            x,
            y,
            width,
            height,
            self._hwnd,
            control_id,
            self._instance,
            None,
        )
        user32.SendMessageW(hwnd, WM_SETFONT, self._font, True)
        return hwnd

    def _create_controls(self) -> None:
        self._control(
            "STATIC",
            "按「開始錄製」後操作一次流程，完成時按「停止並匯出」。\n"
            "錄製期間請不要輸入密碼或私人資料。",
            SS_LEFT,
            20,
            18,
            420,
            45,
            0,
        )
        self._status = self._control(
            "STATIC", "準備就緒", SS_LEFT, 20, 68, 420, 22, 0
        )
        self._start_button = self._control(
            "BUTTON", "開始錄製", BS_PUSHBUTTON, 20, 100, 115, 34, START_ID
        )
        self._stop_button = self._control(
            "BUTTON", "停止並匯出", BS_PUSHBUTTON, 145, 100, 125, 34, STOP_ID
        )
        self._open_button = self._control(
            "BUTTON", "開啟結果資料夾", BS_PUSHBUTTON, 280, 100, 145, 34, OPEN_ID
        )
        self._control(
            "BUTTON", "關閉", BS_PUSHBUTTON, 345, 147, 80, 30, CLOSE_ID
        )
        user32.EnableWindow(self._stop_button, False)
        user32.EnableWindow(self._open_button, False)

    def _set_status(self, text: str) -> None:
        user32.SetWindowTextW(self._status, text)

    def _start(self) -> None:
        self._on_start()
        self._set_status("錄製中…")
        user32.EnableWindow(self._start_button, False)
        user32.EnableWindow(self._stop_button, True)

    def _stop(self) -> None:
        user32.EnableWindow(self._stop_button, False)
        saved_path = self._on_stop()
        user32.EnableWindow(self._start_button, True)
        if not saved_path:
            self._set_status("尚未開始錄製")
            return
        self._last_output = Path(saved_path)
        self._set_status(f"已匯出：{self._last_output.name}")
        user32.EnableWindow(self._open_button, True)
        user32.MessageBoxW(
            self._hwnd,
            f"AI 技能草稿已儲存：\n\n{self._last_output}",
            "錄製完成",
            0x40,
        )

    def _open_output_folder(self) -> None:
        if self._last_output:
            os.startfile(self._last_output.parent)

    def _close(self) -> None:
        if self._closing:
            return
        self._closing = True
        try:
            self._on_quit()
        finally:
            user32.DestroyWindow(self._hwnd)

    def _wndproc(self, hwnd, message, wparam, lparam):
        if message == WM_COMMAND:
            control_id = wparam & 0xFFFF
            try:
                if control_id == START_ID:
                    self._start()
                elif control_id == STOP_ID:
                    self._stop()
                elif control_id == OPEN_ID:
                    self._open_output_folder()
                elif control_id == CLOSE_ID:
                    self._close()
            except Exception as exc:
                user32.MessageBoxW(hwnd, str(exc), "Skill Recorder 錯誤", 0x10)
            return 0
        if message == WM_CLOSE:
            self._close()
            return 0
        if message == WM_DESTROY:
            user32.PostQuitMessage(0)
            return 0
        return user32.DefWindowProcW(hwnd, message, wparam, lparam)

    def show(self) -> None:
        user32.ShowWindow(self._hwnd, SW_SHOW)
        user32.UpdateWindow(self._hwnd)
        message = wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(message), None, 0, 0) > 0:
            user32.TranslateMessage(ctypes.byref(message))
            user32.DispatchMessageW(ctypes.byref(message))
