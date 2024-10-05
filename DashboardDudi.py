#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import geopandas as gpd
import os
os.environ['SHAPE_RESTORE_SHX'] = 'YES'

sns.set(style='dark')

# Call Data And Cleaning
data_customers = pd.read_csv('https://github.com/dudinurdiyans/ProjectDicodingDudi/blob/main/All%20Data/customers_dataset.csv?raw=true')
data_geolocations = pd.read_csv('https://github.com/dudinurdiyans/ProjectDicodingDudi/blob/main/All%20Data/geolocation_dataset.csv?raw=true')
data_order_items = pd.read_csv('https://github.com/dudinurdiyans/ProjectDicodingDudi/blob/main/All%20Data/order_items_dataset.csv?raw=true')
data_order_payments = pd.read_csv('https://github.com/dudinurdiyans/ProjectDicodingDudi/blob/main/All%20Data/order_payments_dataset.csv?raw=true')
data_order_reviews = pd.read_csv('https://github.com/dudinurdiyans/ProjectDicodingDudi/blob/main/All%20Data/order_reviews_dataset.csv?raw=true')
data_orders = pd.read_csv('https://github.com/dudinurdiyans/ProjectDicodingDudi/blob/main/All%20Data/orders_dataset.csv?raw=true')
data_product_category_name_translation = pd.read_csv('https://github.com/dudinurdiyans/ProjectDicodingDudi/blob/main/All%20Data/product_category_name_translation.csv?raw=true')
data_products = pd.read_csv('https://github.com/dudinurdiyans/ProjectDicodingDudi/blob/main/All%20Data/products_dataset.csv?raw=true')
data_sellers = pd.read_csv('https://github.com/dudinurdiyans/ProjectDicodingDudi/blob/main/All%20Data/sellers_dataset.csv?raw=true')
# Mengganti nilai null dengan "tidak mencantumkan"
data_order_reviews['review_comment_title'] = data_order_reviews['review_comment_title'].fillna('tidak mencantumkan')
data_order_reviews['review_comment_message'] = data_order_reviews['review_comment_message'].fillna('tidak mencantumkan')
# Mengganti nilai null dengan "data tidak tersedia"
data_orders['order_approved_at'] = data_orders['order_approved_at'].fillna('data tidak tersedia')
data_orders['order_delivered_carrier_date'] = data_orders['order_delivered_carrier_date'].fillna('data tidak tersedia')
data_orders['order_delivered_customer_date'] = data_orders['order_delivered_customer_date'].fillna('data tidak tersedia')
# Mengganti nilai null dengan "tidak ada data"
data_products['product_category_name'] = data_products['product_category_name'].fillna('tidak ada data')
data_products['product_name_lenght'] = data_products['product_name_lenght'].fillna('tidak ada data')
data_products['product_description_lenght'] = data_products['product_description_lenght'].fillna('tidak ada data')
data_products['product_photos_qty'] = pd.to_numeric(data_products['product_photos_qty'], errors='coerce')
data_products['product_photos_qty'].fillna(0, inplace=True)
data_products['product_weight_g'] = data_products['product_weight_g'].fillna('tidak ada data')
data_products['product_length_cm'] = data_products['product_length_cm'].fillna('tidak ada data')
data_products['product_height_cm'] = data_products['product_height_cm'].fillna('tidak ada data')
data_products['product_width_cm'] = data_products['product_width_cm'].fillna('tidak ada data')


def create_monthly_orders_df(df):
    monthly_orders_df = df.resample(rule='M', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    monthly_orders_df = monthly_orders_df.reset_index()
    monthly_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    
    return monthly_orders_df


# In[ ]:


def create_sum_order_items_df(start_date,end_date):
    # Ensure that 'order_purchase_timestamp' is in datetime format
    data_orders['order_purchase_timestamp'] = pd.to_datetime(data_orders['order_purchase_timestamp'])
    
    # Filter orders by start and end date
    filtered_orders = data_orders[(data_orders['order_purchase_timestamp'] >= start_date) & 
                                  (data_orders['order_purchase_timestamp'] <= end_date)]
    
    # Merge filtered orders with order items and product data
    items = pd.merge(filtered_orders, data_order_items, on="order_id")
    items_products = pd.merge(items, data_products, on="product_id")
    items_products_filtered = items_products[items_products['product_category_name'] != 'tidak ada data']
    sum_order_items_df = items_products_filtered.groupby("product_category_name").product_photos_qty.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df

# In[ ]:


def create_bycity_df(df):
    bycity_df = df.groupby(by="customer_city").customer_id.nunique().reset_index()
    bycity_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    
    return bycity_df


# In[ ]:


def create_by_payment_type_df(df):
    bypayment_type_df = df.groupby(by="payment_type").customer_id.nunique().reset_index()
    bypayment_type_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    
    return bypayment_type_df


# In[ ]:


def create_byorderstatus_df(df):
    byorderstatus_df = df.groupby(by="order_status").customer_id.nunique().reset_index()
    byorderstatus_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    byorderstatus_df['order_status'] = pd.Categorical(byorderstatus_df['order_status'], ["delivered", "shipped", "canceled", "processing", "invoiced"])
    
    return byorderstatus_df


# In[ ]:


all_df = pd.read_csv("https://raw.githubusercontent.com/dudinurdiyans/ProjectDicodingDudi/refs/heads/main/dashboard/all_data.csv")


# In[ ]:


datetime_columns = ["order_purchase_timestamp", "order_estimated_delivery_date"]
all_df.sort_values(by="order_delivered_carrier_date", inplace=True)

 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])


# In[ ]:


min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()
 
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu Penjualan Dudee',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )


# In[ ]:


main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]


# In[ ]:


monthly_orders_df = create_monthly_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(str(start_date),str(end_date))
bycity_df = create_bycity_df(main_df)
bypayment_type_df = create_by_payment_type_df(main_df)
byorderstatus_df = create_byorderstatus_df(main_df)


# In[ ]:


st.header('Dashboard Penjualan Dude :sparkles:')


# In[ ]:


st.subheader('Monthly Orders')
 
col1, col2 = st.columns(2)
with col1:
    total_orders = monthly_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)
with col2:
    total_revenue = format_currency(monthly_orders_df.revenue.sum(), "AUD", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)
    
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    monthly_orders_df["order_purchase_timestamp"],
    monthly_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#000000"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

# Ensure that 'order_purchase_timestamp' is in datetime format
data_orders['order_purchase_timestamp'] = pd.to_datetime(data_orders['order_purchase_timestamp'])

# Filter orders by start and end date
filtered_orders = data_orders[(data_orders['order_purchase_timestamp'] >= str(start_date)) & 
                                (data_orders['order_purchase_timestamp'] <= str(end_date))]
# Menggabungkan data order items dengan orders untuk mendapatkan data timestamp
orders_items = pd.merge(data_order_items, filtered_orders, on="order_id")

# Pastikan kolom 'order_purchase_timestamp' ada dan ubah ke format datetime
orders_items['order_purchase_timestamp'] = pd.to_datetime(orders_items['order_purchase_timestamp'])

# Tambahkan kolom bulan setelah kolom dikonversi ke datetime
orders_items['purchase_month'] = orders_items['order_purchase_timestamp'].dt.to_period('M')

# Menggabungkan dengan produk dan kategori
items_products_category = pd.merge(orders_items, data_products, on="product_id")

# Menghitung total penjualan per kategori
total_sales_per_category = items_products_category.groupby('product_category_name')['price'].sum()

# Mendapatkan 5 kategori produk teratas berdasarkan total penjualan
top_5_categories = total_sales_per_category.nlargest(5).index

# Memfilter hanya untuk 5 kategori teratas
filtered_items = items_products_category[items_products_category['product_category_name'].isin(top_5_categories)]

# Menghitung tren penjualan per kategori per bulan untuk 5 kategori teratas
monthly_sales_top_5 = filtered_items.groupby(['purchase_month', 'product_category_name'])['price'].sum().unstack()

# Plot line chart untuk tren penjualan 5 kategori teratas
plt.figure(figsize=(12,8))
monthly_sales_top_5.plot(marker='o')
plt.xlabel("Bulan")
plt.ylabel("Total Penjualan")
plt.xticks(rotation=45)
plt.grid(True)
plt.show()
st.subheader("Tren Penjualan 5 Kategori Produk Teratas Per Bulan")
st.pyplot(plt)

# Call the function to get the DataFrame
sum_order_items_df = create_sum_order_items_df(str(start_date),str(end_date))
# Plot Best & Worst Performing Product
st.subheader("Best & Worst Performing Product")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

colors = ["#000000", "#C0C0C0", "#C0C0C0", "#C0C0C0", "#C0C0C0"]

# Best sales product category plot
sns.barplot(x="product_photos_qty", y="product_category_name", data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=30)
ax[0].set_title("Best Sales Product Category", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

# Worst sales product category plot
sns.barplot(x="product_photos_qty", y="product_category_name", data=sum_order_items_df.sort_values(by="product_photos_qty", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Sales Product Category", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

# Display the plot
st.pyplot(fig)


# In[4]:


st.subheader("Customer Detail")
col1, col2 = st.columns(2)
with col1:
    # Menghitung jumlah setiap jenis pembayaran
    # Ensure that 'order_purchase_timestamp' is in datetime format
    data_orders['order_purchase_timestamp'] = pd.to_datetime(data_orders['order_purchase_timestamp'])
    
    # Filter orders by start and end date
    filtered_orders = data_orders[(data_orders['order_purchase_timestamp'] >= str(start_date)) & 
                                  (data_orders['order_purchase_timestamp'] <= str(end_date))]
    orders_payments = pd.merge(data_order_payments, filtered_orders, on="order_id")

    payment_counts = orders_payments['payment_type'].value_counts()

# Menampilkan persentase setiap jenis pembayaran
    payment_percentage = (payment_counts / payment_counts.sum()) * 100
    print("Persentase setiap jenis pembayaran:")
    print(payment_percentage)

# Membuat pie chart 
    plt.figure(figsize=(10, 6))
    plt.pie(payment_counts, labels=None, startangle=140, colors=sns.color_palette("Set2"))

# Menambahkan legenda 
    plt.legend(labels=[f'{status}: {count} ({percentage:.1f}%)' for status, count, percentage in zip(payment_counts.index, payment_counts, payment_percentage)],
    title="Jenis Pembayaran",
    loc="best"
)
    plt.title("Jenis Pembayaran")


    st.pyplot(plt)

with col2:
    # Menghitung jumlah setiap status pesanan
    # Ensure that 'order_purchase_timestamp' is in datetime format
    data_orders['order_purchase_timestamp'] = pd.to_datetime(data_orders['order_purchase_timestamp'])
    
    # Filter orders by start and end date
    filtered_orders = data_orders[(data_orders['order_purchase_timestamp'] >= str(start_date)) & 
                                  (data_orders['order_purchase_timestamp'] <= str(end_date))]
    orders_items = pd.merge(filtered_orders, data_order_items, on="order_id")
    
    order_status_counts = orders_items['order_status'].value_counts()

    # Menampilkan persentase setiap status pesanan
    order_status_percentage = (order_status_counts / order_status_counts.sum()) * 100
    print("Persentase setiap status pesanan:")
    print(order_status_percentage)

    # Membuat pie chart
    plt.figure(figsize=(10, 6))
    
    # Membuat pie chart dengan label nama status pesanan
    plt.pie(order_status_counts, 
            labels=None,
            startangle=140, 
            colors=sns.color_palette("Set2"), 
            )

    # Menambahkan legenda dengan status pesanan, jumlah, dan persentase
    plt.legend(labels=[f'{status}: {count} ({percentage:.1f}%)' for status, count, percentage in zip(order_status_counts.index, order_status_counts, order_status_percentage)],
               title="Status Pesanan",
               loc="best")



    plt.title("Perbandingan Status Pesanan")
    st.pyplot(plt)

# Menghitung jumlah pelanggan per kota
customer_city_counts = data_customers['customer_city'].value_counts()

# Mengambil 5 kota teratas 
top_5_cities = customer_city_counts.head(5)
other_cities_count = customer_city_counts[5:].sum()  # Jumlah kota lainnya
top_5_cities['lain-lain'] = other_cities_count  # Menambahkan kategori 'kota lain'


# Membuat pie chart
plt.figure(figsize=(10, 6))
plt.pie(top_5_cities, startangle=140, colors=sns.color_palette("Set2"), autopct='%1.1f%%')

# Menambahkan legenda
plt.legend(
    labels=[f'{label}: {count}' for label, count in zip(top_5_cities.index, top_5_cities)],
    title="Kota Pelanggan",
    loc="best"
)

plt.title("Distribusi Customers Berdasarkan 5 Kota Teratas")
plt.axis('equal')  
st.pyplot(plt)

# Menghitung jumlah seller per kota
seller_city_counts = data_sellers['seller_city'].value_counts().reset_index()
seller_city_counts.columns = ['seller_city', 'count']

# Menggabungkan data geolokasi dengan jumlah seller
merged_data = pd.merge(data_geolocations, seller_city_counts, left_on='geolocation_city', right_on='seller_city', how='left')

# Mengubah DataFrame menjadi GeoDataFrame
gdf = gpd.GeoDataFrame(merged_data, geometry=gpd.points_from_xy(merged_data['geolocation_lng'], merged_data['geolocation_lat']))

# Mengatur ukuran plot 
plt.figure(figsize=(16, 12))  
shapefile_path = os.path.join('ne_110m_admin_0_countries','ne_110m_admin_0_countries.shp')
# Mengambil data peta dunia dari file shapefile 
world = gpd.read_file(shapefile_path)

# Membuat plot
ax = world.plot(color='white', edgecolor='black')

# Menambahkan titik lokasi seller ke peta
gdf.plot(ax=ax, marker='o', color='red', markersize=gdf['count'].fillna(0) * 2, label='Jumlah Seller')  # Ukuran titik diperkecil lebih lanjut

# Menambahkan label
plt.title('Peta Penyebaran Seller Berdasarkan Kota')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.legend()
st.pyplot(plt)

st.caption('Copyright (c) Dudee 2024. All rights reserved.')
# dataset_df.to_csv("all_data.csv", index=False)
# In[ ]:




