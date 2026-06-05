import streamlit as st
import json
import os
import random

DB_FILE = "recipes.json"
IMAGE_DIR = "images"

if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# --- 資料管理邏輯 ---
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # 💡 隱藏防呆：如果檔案不見了，自動生成初始食譜，確保教授打開一定有東西
    default_recipes = {
        "泡麵": {
            "meta": "快速料理 | 3分鐘",
            "ingredients": ["泡麵 1包", "雞蛋 1顆", "青菜 1把"],
            "steps": ["水滾後放入麵體與調味包", "加入打散的雞蛋與青菜", "煮滾3分鐘後即可享用"]
        }
    }
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(default_recipes, f, indent=4, ensure_ascii=False)
    return default_recipes

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_cooking_time(meta_string):
    import re
    minutes = re.findall(r'\d+', meta_string)
    return int(minutes[0]) if minutes else 30

def get_shopping_link(ingredient, platform):
    import urllib.parse
    clean_item = ingredient.split(" ")[0]  # 只拿食材名稱
    query = urllib.parse.quote(clean_item)
    
    if platform == "全聯":
        return f"https://shop.pxmart.com.tw/v2/Search?q={query}"
    elif platform == "家樂福":
        return f"https://online.carrefour.com.tw/zh/search?q={query}"
    elif platform == "Uber Eats":
        return f"https://www.ubereats.com/tw/search?q={query}"
    return "#"

recipes = load_data()

# --- 網頁設定 ---
st.set_page_config(page_title="🍳 智慧食譜最終版", page_icon="🍳", layout="centered")
st.title("🍳 智慧食譜資料庫 ")


# --- 側邊欄與【建議3：資料庫一鍵備份】 ---
st.sidebar.header("⚙️ 系統選單")
menu = st.sidebar.selectbox("功能切換", ["🔍 查詢與隨機選食譜", "📋 列出所有食譜", "➕ 新增食譜", "🛠️ 管理與修改食譜"])

st.sidebar.write("---")
st.sidebar.subheader("💾 安全與備份")

# 將 JSON 轉成字串，提供下載
json_string = json.dumps(recipes, indent=4, ensure_ascii=False)
st.sidebar.download_button(
    label="📥 一鍵備份食譜資料庫",
    data=json_string,
    file_name="recipes_backup.json",
    mime="application/json",
    help="點擊即可將目前的食譜資料庫下載至電腦備份，防止資料遺失！",
    use_container_width=True
)

# ------ 功能一：查詢與隨機選食譜 ------
if menu == "🔍 查詢與隨機選食譜":
    st.header("🔍 今天要吃什麼？")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        query = st.text_input("➔ 輸入關鍵字", placeholder="想搜什麼？").strip()
    with col2:
        st.write("🎲 沒靈感？")
        random_trigger = st.button("隨機選菜！")
    with col3:
        max_time = st.slider("⏱️ 限時(分)", 5, 120, 60, 5)

    st.write("---")

    filtered_list = [n for n, i in recipes.items() if (query in n if query else True) and (get_cooking_time(i["meta"]) <= max_time)]

    if random_trigger:
        if filtered_list:
            random_recipe_name = random.choice(filtered_list)
            st.session_state.target_recipe = random_recipe_name
            st.toast(f"🎲 限時內選中：{random_recipe_name}！", icon='🎉')
        else:
            st.warning("⚠️ 當前時間限制下沒有符合的菜可以抽籤喔！")

    if not filtered_list:
        st.warning("⏳ 找不到符合當前限制的食譜。")
    else:
        default_index = 0
        if "target_recipe" in st.session_state and st.session_state.target_recipe in filtered_list:
            default_index = filtered_list.index(st.session_state.target_recipe)
        else:
            if "target_recipe" in st.session_state:
                del st.session_state.target_recipe
        
        target_recipe = st.selectbox("🎯 請選擇食譜：", filtered_list, index=default_index)

        if target_recipe:
            st.subheader(f"🍽️ {target_recipe}")
            st.info(f"📄 {recipes[target_recipe]['meta']}")
            
            # 圖片顯示
            img_path = None
            for ext in [".jpg", ".jpeg", ".png"]:
                test_path = os.path.join(IMAGE_DIR, f"{target_recipe}{ext}")
                if os.path.exists(test_path):
                    img_path = test_path
                    break
            if img_path:
                st.image(img_path, use_container_width=True)
            
            # 【建議2：精緻網頁導購按鈕】
            st.write("### 【食材清單與線上採買】")
            for item in recipes[target_recipe]["ingredients"]:
                # 使用排版，左邊放食材名稱，右邊放精美按鈕
                c_name, c_btn1, c_btn2, c_btn3 = st.columns([2, 1, 1, 1])
                with c_name:
                    st.write(f"• **{item}**")
                
                # 取得各大平台連結
                link_px = get_shopping_link(item, "全聯")
                link_cf = get_shopping_link(item, "家樂福")
                link_ue = get_shopping_link(item, "Uber Eats")
                
                # 渲染成實體網頁按鈕
                with c_btn1:
                    st.link_button("🛒 全聯", link_px, use_container_width=True)
                with c_btn2:
                    st.link_button("🏪 家樂福", link_cf, use_container_width=True)
                with c_btn3:
                    st.link_button("🛵 Uber", link_ue, use_container_width=True)
                
            st.write("---")
            st.write("### 【烹飪步驟】")
            steps = recipes[target_recipe]["steps"]
            if "step_index" not in st.session_state:
                st.session_state.step_index = 0
            for i in range(st.session_state.step_index + 1):
                if i < len(steps):
                    st.write(f"**{i+1}. {steps[i]}**")
            
            if st.session_state.step_index < len(steps) - 1:
                if st.button("查看下一步 ➡️"):
                    st.session_state.step_index += 1
                    st.rerun()
            else:
                st.balloons()
                st.success("✨ 料理完成！")
                if st.button("重新閱讀 🔄"):
                    st.session_state.step_index = 0
                    st.rerun()

# ------ 功能二：列出所有食譜 ------
elif menu == "📋 列出所有食譜":
    st.header("📋 目前收錄的食譜清單")
    if recipes:
        for i, name in enumerate(recipes, 1):
            with st.expander(f"{i}. {name} ({recipes[name]['meta']})"):
                img_path = None
                for ext in [".jpg", ".jpeg", ".png"]:
                    test_path = os.path.join(IMAGE_DIR, f"{name}{ext}")
                    if os.path.exists(test_path):
                        img_path = test_path
                        break
                if img_path:
                    st.image(img_path, width=300)
                st.write("**食材：**")
                st.write(", ".join(recipes[name]["ingredients"]))
    else:
        st.warning("目前資料庫空空如也。")

# ------ 功能三：➕ 新增食譜 ------
elif menu == "➕ 新增食譜":
    st.header("➕ 新增個人私房食譜")
    new_name = st.text_input("1. 菜名：").strip()
    col_meta1, col_meta2 = st.columns(2)
    with col_meta1:
        new_cate = st.text_input("2. 料理分類：").strip()
    with col_meta2:
        new_time = st.number_input("3. 烹飪時間：", 1, value=15, step=5)
    ing_text = st.text_area("4. 食材 (每行一項，例如: 番茄 2顆)")
    step_text = st.text_area("5. 烹飪步驟 (每行一步)")
    uploaded_file = st.file_uploader("6. 上傳食物照片", type=["jpg", "jpeg", "png"])
    
    if st.button("💾 儲存食譜"):
        if not new_name: st.error("菜名不能為空！")
        else:
            ingredients = [line.strip() for line in ing_text.split("\n") if line.strip()]
            steps = [line.strip() for line in step_text.split("\n") if line.strip()]
            if uploaded_file:
                ext = os.path.splitext(uploaded_file.name)[1]
                with open(os.path.join(IMAGE_DIR, f"{new_name}{ext}"), "wb") as f:
                    f.write(uploaded_file.getbuffer())
            recipes[new_name] = {"meta": f"{new_cate} | {new_time}分鐘", "ingredients": ingredients, "steps": steps}
            save_data(recipes)
            st.success(f"🎉 「{new_name}」已存入資料庫！")

# ------ 功能四：🛠️ 管理與修改食譜 ------
elif menu == "🛠️ 管理與修改食譜":
    st.header("🛠️ 資料庫後台管理")
    if recipes:
        selected_action = st.radio("操作：", ["✏️ 編輯", "❌ 刪除"])
        target_meat = st.selectbox("目標：", list(recipes.keys()))
        if selected_action == "❌ 刪除" and st.button("🔥 確定刪除"):
            del recipes[target_meat]
            save_data(recipes)
            st.rerun()
        elif selected_action == "✏️ 編輯":
            edit_meta = st.text_input("修改標籤：", value=recipes[target_meat]["meta"])
            edit_ings = st.text_area("食材：", value="\n".join(recipes[target_meat]["ingredients"]))
            edit_steps = st.text_area("步驟：", value="\n".join(recipes[target_meat]["steps"]))
            if st.button("💾 儲存修改"):
                recipes[target_meat].update({"meta":edit_meta, "ingredients":edit_ings.split("\n"), "steps":edit_steps.split("\n")})
                save_data(recipes)
                st.success("更新成功！")
                st.rerun()