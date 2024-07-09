import streamlit as st
import pandas as pd
import os


# 데이터 로딩 함수
@st.cache_data
def load_products():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(current_dir, 'products.xlsx')

    df = pd.read_excel(excel_path)
    df.columns = ['index', 'code', 'first_stock', 'last_stock', 'name', 'option1', 'option1_detail',
                  'option2', 'option2_detail', 'stock', 'thumbnail', 'detail_page', 'type', 'price']

    df['first_stock'] = pd.to_datetime(df['first_stock'], format='%Y%m%d', errors='coerce')
    df['last_stock'] = pd.to_datetime(df['last_stock'], format='%Y%m%d', errors='coerce')
    df['first_stock'] = df['first_stock'].apply(lambda x: x if not pd.isnull(x) else None)
    df['last_stock'] = df['last_stock'].apply(lambda x: x if not pd.isnull(x) else None)
    df['type'] = df['type'].fillna('').astype(str)
    df['stock'] = df['stock'].fillna(0).astype(int)
    df['price'] = df['price'].fillna(0).astype(int)

    def get_category(code):
        if code.startswith('MV'):
            return '마블'
        elif code.startswith('FR'):
            return '겨울왕국'
        elif code.startswith('DS'):
            return '디즈니'
        elif code.startswith('MK'):
            return '미키마우스'
        return '기타'

    df['category'] = df['code'].apply(get_category)
    return df


# 메인 애플리케이션
def main():
    st.set_page_config(page_title="제품 카탈로그", layout="wide")
    st.title("제품 카탈로그")

    # 데이터 로드
    products_df = load_products()

    # 사이드바에 필터 추가
    st.sidebar.header("필터")
    categories = sorted(set(products_df['category']))
    selected_category = st.sidebar.selectbox("카테고리 선택", ['전체'] + categories)

    types = sorted(set(products_df['type']))
    selected_type = st.sidebar.selectbox("타입 선택", ['전체'] + types)

    # 검색 기능
    search_query = st.sidebar.text_input("제품 검색")

    # 필터링
    if selected_category != '전체':
        products_df = products_df[products_df['category'] == selected_category]
    if selected_type != '전체':
        products_df = products_df[products_df['type'] == selected_type]
    if search_query:
        products_df = products_df[products_df['name'].str.contains(search_query, case=False) |
                                  products_df['code'].str.contains(search_query, case=False)]

    # 제품 표시
    for _, product in products_df.iterrows():
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(product['thumbnail'], width=200)
        with col2:
            st.subheader(product['name'])
            st.write(f"코드: {product['code']}")
            st.write(f"가격: {product['price']:,}원")
            st.write(f"재고: {product['stock']}개")

            # 상세 정보 열기/닫기 버튼
            if st.button(
                    f"상세 정보 {'닫기' if st.session_state.get(f'show_details_{product["code"]}', False) else '보기'} ({product['code']})"):
                st.session_state[f'show_details_{product["code"]}'] = not st.session_state.get(
                    f'show_details_{product["code"]}', False)

            # 상세 정보 표시
            if st.session_state.get(f'show_details_{product["code"]}', False):
                show_product_detail(product)


def show_product_detail(product):
    st.subheader(f"{product['name']} 상세 정보")
    st.image(product['thumbnail'], width=300)
    st.write(f"코드: {product['code']}")
    st.write(f"가격: {product['price']:,}원")
    st.write(f"재고: {product['stock']}개")
    st.write(f"옵션1: {product['option1']} - {product['option1_detail']}")
    st.write(f"옵션2: {product['option2']} - {product['option2_detail']}")
    st.write(f"첫 입고일: {product['first_stock']}")
    st.write(f"마지막 입고일: {product['last_stock']}")
    st.write(f"타입: {product['type']}")
    st.write(f"카테고리: {product['category']}")

    # 상세 이미지 표시
    st.subheader("상세 설명")
    for image_url in product['detail_page'].split(','):
        st.image(image_url.strip(), use_column_width=True)


if __name__ == "__main__":
    main()