# -*- coding: utf-8 -*-
"""
Ollama 可视化模型选择面板（阶段2新增）

说明：
- 本模块属于 Streamlit WebUI 前端代码，不新增、不修改任何后端接口；
- 模型列表通过本地 Ollama 服务的原生接口 /api/tags 自动读取；
- 模型切换复用项目原有模型配置逻辑：
  1) 与“模型配置”弹窗共用会话键 llm_model（chat_box.context["llm_model"]）；
  2) 选中模型若未注册，则写入项目已有的 model_settings.yaml（复用 Settings 自带的
     create_template_file 持久化能力），后端进程读取到配置文件变化后会自动热更新，
     从而保证选中的 Ollama 模型可被后端正确路由。
"""

import httpx
import streamlit as st

from chatchat.settings import Settings, PlatformConfig
from chatchat.server.utils import get_config_models, get_config_platforms

# 本地 Ollama 服务默认地址（项目 model_settings 中 ollama 平台未配置时回退使用）
OLLAMA_DEFAULT_BASE_URL = "http://127.0.0.1:11434"


def get_ollama_base_url() -> str:
    """
    从项目已有的模型平台配置（MODEL_PLATFORMS）中定位 ollama 平台，
    取其 api_base_url（去掉 /v1 后缀）作为 Ollama 服务地址；
    未配置 ollama 平台时回退到本地默认地址 127.0.0.1:11434。
    """
    for platform in get_config_platforms().values():
        if platform.get("platform_type") == "ollama":
            base = (platform.get("api_base_url") or "").strip()
            if base:
                # 平台配置指向 openai 兼容地址（.../v1），面板访问原生接口需去掉 /v1
                return base.removesuffix("/v1").rstrip("/")
    return OLLAMA_DEFAULT_BASE_URL


@st.cache_data(ttl=30, show_spinner=False)
def list_ollama_models(base_url: str) -> dict:
    """
    请求本地 Ollama 服务原生接口 /api/tags，自动读取本机已安装的模型列表。
    返回结构：{"ok": 是否连通, "models": [模型信息列表], "msg": 错误说明}
    使用 st.cache_data 做 30 秒短缓存，避免每次页面交互都重新请求 Ollama。
    """
    try:
        resp = httpx.get(f"{base_url}/api/tags", timeout=3.0)
        resp.raise_for_status()
        raw = resp.json().get("models", []) or []
        models = []
        for m in raw:
            details = m.get("details", {}) or {}
            # capabilities 字段位于模型对象顶层（部分旧版本在 details 内或缺失）
            capabilities = m.get("capabilities") or details.get("capabilities") or []
            # 兼容不同版本的 Ollama：无 capabilities 字段时按模型家族粗略判断
            if not capabilities:
                capabilities = (
                    ["embedding"] if details.get("family") in ("bert",) else ["completion"]
                )
            models.append(
                {
                    "name": m.get("name") or m.get("model") or "",
                    "size": m.get("size", 0),
                    "parameter_size": details.get("parameter_size", ""),
                    "quantization_level": details.get("quantization_level", ""),
                    "modified_at": (m.get("modified_at") or "")[:10],
                    "capabilities": capabilities,
                }
            )
        return {"ok": True, "models": models, "msg": ""}
    except Exception as e:
        return {"ok": False, "models": [], "msg": str(e)}


def register_ollama_model_to_config(model_name: str) -> bool:
    """
    将选中的 Ollama 模型同步进项目原有的模型配置逻辑：
    即 MODEL_PLATFORMS 中 ollama 平台的 llm_models 列表（复用项目自带配置机制）。

    - 若模型已注册在任意平台的 llm 列表中，则无需重复写入；
    - 内存更新后通过 Settings 自带的 create_template_file 持久化到 model_settings.yaml
      （与 `chatchat init` 生成配置文件的方式一致）；
    - 后端进程内置的配置热更新机制（pydantic_settings_file 基于文件修改时间的缓存）
      感知到配置文件变化后会自动重新加载，因此无需新增任何后端接口。

    返回：是否发生了新增写入。
    """
    # 模型已在项目配置的任意平台注册过（可被路由）则直接跳过
    if model_name in get_config_models(model_type="llm"):
        return False

    # 先取一次 Settings.model_settings 的引用，避免写入过程中配置热重载替换实例
    model_settings = Settings.model_settings
    changed = False
    for platform in model_settings.MODEL_PLATFORMS:
        if platform.platform_type == "ollama":
            # llm_models 字段可能为字面量 "auto" 或列表，统一转为列表后追加
            if platform.llm_models == "auto":
                platform.llm_models = [model_name]
                changed = True
            elif model_name not in platform.llm_models:
                platform.llm_models.append(model_name)
                changed = True

    if changed:
        # 持久化方式与 `chatchat init` 完全一致（保留配置文件注释结构）
        model_settings.create_template_file(
            sub_comments={
                "MODEL_PLATFORMS": {"model_obj": PlatformConfig(), "is_entire_comment": True}
            },
            write_file=True,
        )
    return changed


def _model_label(m: dict) -> str:
    """
    构造下拉框展示文本：模型名（参数规模 · 量化级别 · 更新日期）
    """
    parts = [x for x in (m["parameter_size"], m["quantization_level"], m["modified_at"]) if x]
    return f"{m['name']}（{' · '.join(parts)}）" if parts else m["name"]


def ollama_model_panel(
    current_model: str = "",
    save_session_fn=None,
    rerun_fn=None,
):
    """
    渲染 Ollama 可视化模型选择面板（位于多功能对话页侧边栏的“Ollama 模型”标签页）。

    参数：
    - current_model: 当前会话使用的模型名（来自 chat_box.context，与“模型配置”弹窗共用）；
    - save_session_fn: 复用 dialogue 页的会话保存函数 save_session；
    - rerun_fn: 复用 dialogue 页的 rerun 函数（保存会话并刷新页面）。
    """
    base_url = get_ollama_base_url()
    st.caption(f"Ollama 服务地址：`{base_url}`")

    info = list_ollama_models(base_url)

    # 服务离线时的友好提示
    if not info["ok"]:
        st.error(f"无法连接本地 Ollama 服务（{base_url}），请确认 Ollama 已启动。")
        if st.button("🔄 重新检测", key="ollama_refresh", use_container_width=True):
            list_ollama_models.clear()
            st.rerun()
        return

    models = info["models"]
    # 区分可对话的 LLM 与 Embedding 模型：面板仅提供 LLM 供切换，Embedding 仅做展示
    llm_models = [m for m in models if "embedding" not in m["capabilities"]]
    embed_models = [m for m in models if "embedding" in m["capabilities"]]

    st.success(f"已连接 Ollama，共检测到 {len(models)} 个本地模型")
    if st.button("🔄 刷新模型列表", key="ollama_refresh", use_container_width=True):
        list_ollama_models.clear()
        st.rerun()

    if not llm_models:
        st.warning("本地 Ollama 未发现可对话的 LLM 模型，请先执行 `ollama pull <模型名>` 拉取模型。")
    else:
        labels = [_model_label(m) for m in llm_models]
        name2model = {_model_label(m): m for m in llm_models}
        # 若当前会话模型就在本地列表中，则默认选中它
        current_label = next((_model_label(m) for m in llm_models if m["name"] == current_model), None)
        index = labels.index(current_label) if current_label in labels else 0
        selected_label = st.selectbox(
            "选择本地 Ollama 模型",
            options=labels,
            index=index,
            key="ollama_selected_model",
        )
        selected = name2model[selected_label]

        # 应用按钮：复用项目原有模型配置逻辑完成“切换模型”
        if st.button(
            "应用为当前对话模型",
            key="ollama_apply",
            type="primary",
            use_container_width=True,
        ):
            # 第一步：将选中的模型同步进项目模型配置（若未注册），保证后端可正确路由
            registered = register_ollama_model_to_config(selected["name"])
            if registered:
                st.toast(f"已将 {selected['name']} 同步到模型配置，服务端将自动热更新。", icon="🧩")
            # 第二步：与“模型配置”弹窗共用会话键 llm_model（原有模型配置通道）
            st.session_state["llm_model"] = selected["name"]
            # 第三步：保存会话并刷新页面，使新模型立即生效
            if save_session_fn:
                save_session_fn()
            if rerun_fn:
                rerun_fn()
            else:
                st.rerun()

    if embed_models:
        st.caption("检测到 Embedding 模型：" + "、".join(m["name"] for m in embed_models))

    if current_model:
        st.caption(f"当前对话模型：`{current_model}`")
