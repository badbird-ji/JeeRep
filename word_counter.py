import streamlit as st 
 
def main():
    st.title(" 文字统计工具")
    
    # 创建文本输入区域 
    text = st.text_area(" 请输入要统计的文字内容", height=200)
    
    # 添加统计按钮 
    if st.button(" 统计字数"):
        # 计算字数（去除首尾空格）
        count = len(text.strip()) 
        
        # 显示结果（使用不同颜色突出显示）
        st.success(f"** 字数统计结果**: {count}") 
        
        # 额外统计信息（增强功能）
        col1, col2 = st.columns(2) 
        with col1:
            st.metric(" 字符数（含空格）", len(text))
        with col2:
            st.metric(" 字符数（不含空格）", len(text.replace("  ", "")))
 
if __name__ == "__main__":
    main()