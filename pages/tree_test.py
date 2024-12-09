import streamlit as st
from streamlit_markmap import markmap

st.set_page_config(page_title="markmap", layout="wide")

with open('data/tree_data.md', encoding='utf-8') as fp:
    md = fp.read()

markmap(md,height=400)



data2 = """# A """
data22 = """\n## AA2
### AAA
#### AAAA
##### AAAAA"""

data3 = """
# B
## BB
## BC
### BCA"""

markmap(data2 + data22 + data3,height=400)