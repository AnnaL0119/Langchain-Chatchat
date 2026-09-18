import sys

import streamlit as st
import streamlit_antd_components as sac

from chatchat import __version__
from chatchat.server.utils import api_address
from chatchat.webui_pages.dialogue.dialogue import  dialogue_page
from chatchat.webui_pages.kb_chat import kb_chat
from chatchat.webui_pages.mcp import mcp_management_page
from chatchat.webui_pages.knowledge_base.knowledge_base import knowledge_base_page
from chatchat.webui_pages.utils import *

api = ApiRequest(base_url=api_address())

if __name__ == "__main__":
    is_lite = "lite" in sys.argv  # TODO: remove lite mode

    st.set_page_config(
        "Langchain-Chatchat WebUI",
        get_img_base64("chatchat_icon_blue_square_v2.png"),
        initial_sidebar_state="expanded",
        menu_items={
            "Get Help": "https://github.com/chatchat-space/Langchain-Chatchat",
            "Report a bug": "https://github.com/chatchat-space/Langchain-Chatchat/issues",
            "About": f"""欢迎使用 Langchain-Chatchat WebUI {__version__}！""",
        },
        layout="centered",
    )

    # 使用以下样式设置应用为宽屏模式，并通过 HTML/CSS 调整侧边栏宽度、
    # 注入柔和粉色主题美化与移动端适配样式
    st.markdown(
        """
        <style>
        [data-testid="stSidebarUserContent"] {
            padding-top: 20px;
        }
        .block-container {
            padding-top: 25px;
        }
        [data-testid="stBottomBlockContainer"] {
            padding-bottom: 20px;
        }

        /* ================= 粉色主题美化（仅展示层，不影响业务逻辑） ================= */

        /* 侧边栏：浅粉背景 + 右侧柔粉描边 */
        [data-testid="stSidebar"] {
            background-color: #FBEAF1;
            border-right: 1px solid #F5C9DB;
        }

        /* 全局按钮：柔和粉色系，圆角 + 悬停动效 */
        .stButton > button,
        .stDownloadButton > button {
            border-radius: 10px;
            border: 1px solid #F0B7CD;
            color: #B34771;
            background-color: #FFF3F7;
            transition: all 0.2s ease-in-out;
        }
        .stButton > button:hover,
        .stDownloadButton > button:hover {
            border-color: #EC7CA9;
            background-color: #FCE4EE;
            color: #9C3159;
            box-shadow: 0 2px 8px rgba(236, 124, 169, 0.25);
        }

        /* 主按钮（primary）：粉色填充样式 */
        .stButton > button[kind="primary"],
        .stDownloadButton > button[kind="primary"] {
            background-color: #EC7CA9;
            border-color: #EC7CA9;
            color: #FFFFFF;
        }
        .stButton > button[kind="primary"]:hover {
            background-color: #E06A9B;
            border-color: #E06A9B;
        }

        /* 对话气泡：用户与 AI 消息卡片化，柔粉描边 */
        [data-testid="stChatMessage"] {
            background-color: #FFF9FB;
            border: 1px solid #F7DCE7;
            border-radius: 12px;
            padding: 8px 12px;
            margin-bottom: 8px;
        }

        /* 文本输入框、选择框：聚焦时粉色描边 */
        .stTextInput input:focus,
        .stTextArea textarea:focus,
        .stNumberInput input:focus {
            border-color: #EC7CA9 !important;
            box-shadow: 0 0 0 1px #EC7CA9;
        }

        /* 标签页（tabs）激活态文字使用主粉色 */
        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] p {
            color: #D4578A;
        }

        /* ================= 文件上传组件内置英文提示汉化 =================
           说明：以下文本由 Streamlit 前端库内置渲染，无法直接修改源码，
           因此采用 CSS 文本替换（原文字号置零 + 伪元素显示中文）的方式汉化 */
        [data-testid="stFileUploaderDropzone"] span {
            font-size: 0 !important;
        }
        [data-testid="stFileUploaderDropzone"] span::after {
            content: "拖拽文件到此处";
            font-size: 0.9rem;
        }
        [data-testid="stFileUploaderDropzone"] small {
            font-size: 0 !important;
        }
        [data-testid="stFileUploaderDropzone"] small::after {
            content: "单文件不超过 200MB";
            font-size: 0.72rem;
            opacity: 0.65;
        }
        [data-testid="stFileUploaderDropzone"] button {
            font-size: 0 !important;
        }
        [data-testid="stFileUploaderDropzone"] button::after {
            content: "浏览文件";
            font-size: 0.875rem;
        }

        /* ================= 移动端适配（小屏幕：≤768px 手机/平板竖屏） ================= */
        @media (max-width: 768px) {
            /* 缩减页面上下留白，为内容腾出更多空间 */
            .block-container {
                padding-top: 12px;
                padding-bottom: 60px;
            }

            /* 侧边栏在手机上收起时默认铺满一半宽度，保证可点按 */
            [data-testid="stSidebar"] {
                min-width: 260px;
            }

            /* 多列布局在窄屏下自动换行、逐列堆叠，避免横向滚动 */
            [data-testid="stHorizontalBlock"] {
                flex-wrap: wrap;
            }
            [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
                min-width: 45%;
            }

            /* 按钮在手机上加大触控高度 */
            .stButton > button,
            .stDownloadButton > button {
                min-height: 40px;
                font-size: 15px;
            }

            /* 对话输入框字号加大，减少手机端误触 */
            [data-testid="stChatInput"] textarea {
                font-size: 16px !important;
            }

            /* 表格/网格容器允许横向滑动，避免页面被撑破 */
            [data-testid="stDataFrame"] {
                overflow-x: auto;
            }

            /* 全局禁止横向溢出 */
            .stApp, .block-container {
                overflow-x: hidden;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.image(
            get_img_base64("logo-long-chatchat-trans-v2.png"), use_column_width=True
        )
        st.caption(
            f"""<p align="right">当前版本：{__version__}</p>""",
            unsafe_allow_html=True,
        )

        selected_page = sac.menu(
            [
                sac.MenuItem("多功能对话", icon="chat"),
                sac.MenuItem("RAG 对话", icon="database"),
                sac.MenuItem("知识库管理", icon="hdd-stack"),
                sac.MenuItem("MCP 管理", icon="hdd-stack"),
            ],
            key="selected_page",
            open_index=0,
        )

        sac.divider()

    if selected_page == "知识库管理":
        knowledge_base_page(api=api, is_lite=is_lite)
    elif selected_page == "RAG 对话":
        kb_chat(api=api)
    elif selected_page == "MCP 管理":
        mcp_management_page(api=api)
    else:
        dialogue_page(api=api, is_lite=is_lite)
