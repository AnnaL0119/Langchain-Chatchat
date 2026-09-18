# -*- coding: utf-8 -*-
"""
文件上传前端校验工具（阶段3新增）

说明：
- 本模块属于 Streamlit WebUI 前端代码，不新增、不修改任何后端接口；
- 用于在调用项目原有上传接口（upload_kb_docs / upload_temp_docs 等）之前，
  在前端对文件做类型、大小、空文件等基础校验，并给出中文友好提示；
- 大小上限与 .streamlit/config.toml 中的 maxUploadSize = 200 保持一致；
- 上传动作本身仍复用项目原有后端接口，本模块只做"上传前的拦截与提示"。
"""

from typing import List, Optional, Tuple

# 上传文件大小上限（MB），与 .streamlit/config.toml 的 maxUploadSize 保持一致
MAX_UPLOAD_SIZE_MB = 200


def format_file_size(size_bytes) -> str:
    """
    将字节数转换为易读的中文大小描述（如 1.5 MB / 300 KB）
    """
    try:
        size = float(size_bytes)
    except (TypeError, ValueError):
        return "未知大小"
    if size >= 1024 * 1024:
        return f"{size / 1024 / 1024:.1f} MB"
    if size >= 1024:
        return f"{size / 1024:.0f} KB"
    return f"{size:.0f} B"


def validate_uploaded_files(
    files,
    allowed_exts: Optional[List[str]] = None,
    max_size_mb: int = MAX_UPLOAD_SIZE_MB,
) -> Tuple[list, List[str]]:
    """
    对待上传的文件列表做前端基础校验（阶段3新增，中文友好提示）

    校验项：
    1. 文件内容是否为空（0 字节）；
    2. 文件大小是否超过上限（默认 200MB，与 Streamlit 上传配置一致）；
    3. 文件扩展名是否在允许列表内（对 file_uploader type 过滤的二次防御，
       防止改名伪装扩展名的文件进入上传流程）。

    参数：
    - files: st.file_uploader 返回的文件（单个或列表）；
    - allowed_exts: 允许的扩展名列表（如 ["bmp", "jpg", "png"]），None 表示不校验类型；
    - max_size_mb: 大小上限（MB）。

    返回：
    - (通过校验的文件列表, 中文错误提示列表)；错误列表非空时不应继续调用上传接口。
    """
    valid_files = []
    errors = []
    # 兼容单个文件与文件列表两种入参
    file_list = list(files) if isinstance(files, (list, tuple)) else [files]

    for f in file_list:
        if f is None:
            continue
        name = getattr(f, "name", "未知文件")
        size = getattr(f, "size", None)

        # 校验 1：空文件拦截
        if size == 0:
            errors.append(f"「{name}」文件内容为空，请更换有效文件。")
            continue

        # 校验 2：大小上限拦截
        if isinstance(size, (int, float)) and size > max_size_mb * 1024 * 1024:
            errors.append(
                f"「{name}」大小为 {format_file_size(size)}，"
                f"超过单文件上限 {max_size_mb}MB，请压缩或拆分后再上传。"
            )
            continue

        # 校验 3：扩展名二次防御（大小写不敏感）
        if allowed_exts:
            allowed = [str(e).lower().lstrip(".") for e in allowed_exts]
            ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
            if ext not in allowed:
                errors.append(
                    f"「{name}」文件类型不受支持，仅允许：{('、'.join(allowed))}。"
                )
                continue

        valid_files.append(f)

    return valid_files, errors


def get_upload_failure_msg(ret, action: str = "文件上传") -> str:
    """
    将项目原有上传接口的返回结果翻译为中文失败提示（阶段3新增）

    上传成功时返回空字符串；失败时返回可直接用于 st.error 的中文信息。
    覆盖两类场景：
    1. 接口返回 None（重试后仍无法连接后端服务）；
    2. 接口返回 code != 200 的 BaseResponse（使用后端返回的中文 msg，缺失时给出兜底文案）。
    """
    if ret is None:
        return f"{action}失败：无法连接后端服务，请确认 API 服务（默认端口 7861）已启动后重试。"
    if isinstance(ret, dict):
        code = ret.get("code")
        msg = ret.get("msg") or ret.get("errorMsg") or ""
        if code not in (None, 200):
            if msg:
                return f"{action}失败：{msg}"
            return f"{action}失败：服务器返回异常（code={code}），请查看后端服务日志。"
    return ""
