import streamlit as st 
import pandas as pd
import plotly.express as px 
import os
import warnings
warnings.filterwarnings('ignore')

#The :bar_chart: icon is an emoji, taken from the streamlit emoji official website 
st.set_page_config(page_title = 'Dashy!!', page_icon = ":barchart:", layout = "wide")

st.title(":bar_chart: Sample SuperStore EDA")
st.markdown('<style>div.block-container{padding-top: 2rem;}</style>', unsafe_allow_html = True)

#Bar to upload the file
f1 = st.file_uploader(":file_folder: Upload a file", type = (["csv","txt", "xlsx","xls"]))
if f1 is not None:
    filename = f1.name
    st.write(filename)
    df = pd.read_csv(filename, encoding = 'ISO-8859-1')
else:
    df = pd.read_csv("Superstore.csv")
    
#Date picker start to end
col1, col2 = st.columns((2))
df["Order Date"] = pd.to_datetime(df["Order Date"],dayfirst=True)

#getting the min and max date
startDate = pd.to_datetime(df["Order Date"], dayfirst=True).min()
endDate = pd.to_datetime(df["Order Date"],dayfirst=True).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date-", startDate))
    
with col2:
    date2 = pd.to_datetime(st.date_input("End Date-", endDate))
    
df = df[(df["Order Date"]>= date1)& (df["Order Date"]<= date2)].copy()

#To create a sidebar
st.sidebar.header("Choose your filter: ")
#Create for Region
region = st.sidebar.multiselect("Pick your Poison City", df["Region"].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]

#Create for State
state = st.sidebar.multiselect("Pick your state Poison", df2["State"].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(state)]
    
#Create for City
city = st.sidebar.multiselect("Pick your City Poison",df3["City"].unique())

#Filter the data based on region, State and City
if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif state and city:
    filtered_df = df3[df["State"].isin(state) & df3["City"].isin(city)]
elif region and city:
    filtered_df = df3[df["Region"].isin(region) & df3["City"].isin(city)]
elif region and state:
    filtered_df = df3[df["Region"].isin(region) & df3["State"].isin(state)]
elif city:
    filtered_df = df3[df3["City"].isin(city)]
else:
    filtered_df = df3[df3["Region"].isin(region) & df3["State"].isin(state) & df3["City"].isin(city)]
    
category_df = filtered_df.groupby(by = ["Category"], as_index = False)["Sales"].sum()
region_df = filtered_df.groupby(by = ["Region"], as_index = False)["Sales"].sum()

with col1:
    st.subheader("Category wise Sales")
    fig = px.bar(category_df, x = "Category", y = "Sales", text = ['${:,.2f}'.format(x) for x in category_df["Sales"]], template = "seaborn")
    st.plotly_chart(fig, use_container_width= True, height = 200)
    
with col2:
    st.subheader("Region wise Sales")
    fig = px.pie(filtered_df, values = 'Sales', names = "Region", hole = 0.5)
    fig.update_traces(text = filtered_df["Region"], textposition = "outside")
    st.plotly_chart(fig,use_container_width=True)
    
#To create a download button for the data 
cl1, cl2 = st.columns(2)
with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap = "Greens"))
        csv_files = category_df.to_csv(index = False).encode("utf-8")
        st.download_button("Download Data", data = csv_files, file_name = "Category.csv", mime = "text/csv", help = 'Click here to Download the data as a csv file')
    
with cl2:
    with st.expander("Region_ViewData"):
        st.write(region_df.style.background_gradient(cmap = "coolwarm"))
        csv_files = region_df.to_csv(index = False).encode("utf-8")
        st.download_button("Download Data", data = csv_files, file_name = "Region.csv", mime = "text/csv", help = 'Click here to Download the data as a csv file')
        

#Visualize the data using the Time Series Analysis based on MM-YYYY - Making a Line graph
filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader('Time Series Analysis')

linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y: %b"))["Sales"].sum()).reset_index()
fig2 = px.line(linechart, x = "month_year", y ="Sales", labels = {"Sales": "Amount"}, height = 500, width = 1000, template = "gridon")
st.plotly_chart(fig2, use_container_width= True)

#To create a download button for the Time Series Analysis graph
#In order to get the table horizontally we can Transpose the linechart (in the st.write line)
with st.expander("View Data of Time Series Analysis: "):
    st.write(linechart.style.background_gradient(cmap = "twilight"))
    csv_files = linechart.to_csv(index = False).encode("utf-8")
    st.download_button('Download Here', data = csv_files, file_name = "TSA_graph.csv", mime = "text/csv", help = "See down here you Idiot")

#To create a TreeMap based on Region, Category, Sub-Category
st.subheader("To View the Heirarchial Sales using TreeMap ")
fig3 = px.treemap(filtered_df, path = ['Region', 'Category', 'Sub-Category'], values = "Sales", hover_data= ['Sales'], color = 'Sub-Category')
fig3.update_layout(width = 1000, height = 850)
st.plotly_chart(fig3,use_container_width= True)

#Segment-wise and Category-wise Sales
chart1, chart2 = st.columns((2))
with chart1:
    st.subheader("Segment wise Sales")
    fig = px.pie(filtered_df, values = 'Sales', names = 'Segment', template = 'simple_white')
    fig.update_traces(text = filtered_df['Segment'], textposition = 'inside')
    st.plotly_chart(fig, use_container_width= True)
    
with chart2:
    st.subheader("Segment wise Category")
    fig2 = px.pie(filtered_df, values = 'Sales', names = 'Category', template = 'presentation')
    fig2.update_traces(text = filtered_df['Category'], textposition = 'auto')
    st.plotly_chart(fig2, use_container_width= True)

#Specific columns in a data format
import plotly.figure_factory as ff 
st.subheader(":point_right: Month wise Sub-Category Sales Summary")
with st.expander("Summary Table"):
    df_sample = df[0:5][["Region","State","City","Category","Sales","Profit","Quantity"]]
    fig = ff.create_table(df_sample, colorscale = "earth")
    st.plotly_chart(fig, use_container_width=True)
    
    
    st.markdown("Month wise Sub-Category Table")
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_year = pd.pivot_table(data= filtered_df, values = "Sales", index = ["Sub-Category"], columns = "month")
    st.write(sub_category_year.style.background_gradient(cmap = "YlGnBu"))
    
#ScatterPlot - To show b/w Sales and Profit
scatter = st.columns(1)[0]
with scatter:
    st.subheader("Sales wise Profit")
    fig = px.scatter(filtered_df, x = "Sales", y = "Profit", size = "Quantity",template="plotly_dark", title="Relationship between the Sales and Profits")
    fig.update_layout(width = 900, height = 850)
    st.plotly_chart(fig, use_container_width= True)
    
#To create a Download button of the ScatterPlot Data
with st.expander("View Data"):
    trimmed_Data = filtered_df.iloc[:500,1:20:2] 
    st.write(trimmed_Data.style.background_gradient(cmap= "Blues"), index = False)
    csv_download = trimmed_Data.to_csv(index = False).encode('utf-8')
    st.download_button('Download Here', data = csv_download, file_name = 'trimmed_file.csv',mime = 'text/csv')
    
#Download the Orginal DataSet
st.subheader("Download the Original DataSet")
csv = df.to_csv(index = False).encode('utf-8')
st.download_button('Download Data', data = csv, file_name = 'Original_Data.csv',mime = 'text/csv')

    
