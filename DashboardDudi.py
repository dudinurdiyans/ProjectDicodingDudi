#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')


# In[2]:


def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_approved_at').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    
    return daily_orders_df


# In[ ]:


def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_category_name").quantity_x.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df


# In[ ]:


def create_bycity_df(df):
    bycity_df = df.groupby(by="customer_city").customer_id.nunique().reset_index()
    bycity_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    
    return bycity_df


# In[ ]:


def create_bypayment_type_df(df):
    bypayment_type_df = df.groupby(by="gender").customer_id.nunique().reset_index()
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


all_df = pd.read_csv("https://github.com/dudinurdiyans/ProjectDicodingDudi/blob/main/all_data.csv")


# In[ ]:


datetime_columns = ["order_delivered_carrier_date", "order_delivered_customer_date"]
all_df.sort_values(by="order_delivered_carrier_date", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])


# In[ ]:


min_date = all_df["order_delivered_carrier_date"].min()
max_date = all_df["order_delivered_carrier_date"].max()
 
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )


# In[ ]:


main_df = all_df[(all_df["order_date"] >= str(start_date)) & 
                (all_df["order_date"] <= str(end_date))]


# In[ ]:


daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
bycity_df = create_bycity_df(main_df)
bypayment_type_df = create_by_payment_type_df(main_df)
byorderstatus_df = create_byorderstatus_df(main_df)


# In[ ]:


st.header('Dicoding Collection Dashboard :sparkles:')


# In[ ]:


st.subheader('Daily Orders')
 
col1, col2 = st.columns(2)
with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)
with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "AUD", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)
# Menggabungkan data order items dengan orders untuk mendapatkan data timestamp
orders_items = pd.merge(data_order_items, data_orders, on="order_id")

# Pastikan kolom 'order_purchase_timestamp' ada dan ubah ke format datetime
orders_items['order_purchase_timestamp'] = pd.to_datetime(orders_items['order_purchase_timestamp'])

# Tambahkan kolom bulan setelah kolom dikonversi ke datetime
orders_items['purchase_month'] = orders_items['order_purchase_timestamp'].dt.to_period('M')

# Menggabungkan dengan produk dan kategori
items_products_category = pd.merge(orders_items, data_products, on="product_id")
items_products_category = pd.merge(items_products_category, data_product_category_name_translation, on="product_category_name")

# Menghitung total penjualan per kategori
total_sales_per_category = items_products_category.groupby('product_category_name_english')['price'].sum()

# Mendapatkan 5 kategori produk teratas berdasarkan total penjualan
top_5_categories = total_sales_per_category.nlargest(5).index

# Memfilter hanya untuk 5 kategori teratas
filtered_items = items_products_category[items_products_category['product_category_name_english'].isin(top_5_categories)]

# Menghitung tren penjualan per kategori per bulan untuk 5 kategori teratas
monthly_sales_top_5 = filtered_items.groupby(['purchase_month', 'product_category_name_english'])['price'].sum().unstack()

# Plot line chart untuk tren penjualan 5 kategori teratas
plt.figure(figsize=(12,8))
monthly_sales_top_5.plot(marker='o')
plt.title("Tren Penjualan 5 Kategori Produk Teratas Per Bulan")
plt.xlabel("Bulan")
plt.ylabel("Total Penjualan")
plt.xticks(rotation=45)
plt.grid(True)
plt.show()


# In[3]:


st.subheader("Best & Worst Performing Product")
# Menggabungkan data items dan produk dengan kategori
items_products = pd.merge(data_order_items, data_products, on="product_id")
items_products_category = pd.merge(items_products, data_product_category_name_translation, on="product_category_name")

# Menghitung penjualan per kategori untuk semua kategori
all_category_sales = items_products_category['product_category_name_english'].value_counts()

# Mengambil 5 kategori dengan jumlah penjualan tertinggi
top_category_sales = all_category_sales.nlargest(5)

# Menampilkan 5 kategori tertinggi
print("5 Kategori dengan Penjualan Tertinggi:")
print(top_category_sales)

# Menggunakan subplots untuk membuat figure dan axes
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 6))

# Menggunakan palet warna "viridis" untuk grafik
sns.barplot(x=top_category_sales.values, y=top_category_sales.index, palette="viridis", ax=ax)

# Menetapkan judul dan label sumbu
ax.set_title("5 Kategori Produk dengan Penjualan Tertinggi", fontsize=20)
ax.set_xlabel("Jumlah Penjualan", fontsize=15)
ax.set_ylabel("Kategori Produk", fontsize=15)

# Menampilkan grafik
plt.show()

# Plot kedua

# Menghitung penjualan per kategori untuk semua kategori
all_category_sales = items_products_category['product_category_name_english'].value_counts()

# Mengambil 5 kategori dengan jumlah penjualan terendah dan mengurutkannya secara ascending
lowest_category_sales = all_category_sales.nsmallest(5)

# Menampilkan 5 kategori terendah
print("5 Kategori dengan Penjualan Terendah:")
print(lowest_category_sales)

# Menggunakan subplots untuk membuat figure dan axes
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

# Menyortir berdasarkan jumlah penjualan dan memilih 5 kategori terendah
sorted_lowest_sales = lowest_category_sales.sort_values(ascending=True)

# Menggunakan palet warna "viridis"
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

# Plot bar chart untuk 5 kategori terendah
sns.barplot(x=sorted_lowest_sales.values, y=sorted_lowest_sales.index, palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Jumlah Penjualan", fontsize=30)
ax[1].invert_xaxis()  # Membalik sumbu X
ax[1].yaxis.set_label_position("right")  # Memindahkan label sumbu Y ke kanan
ax[1].yaxis.tick_right()  # Memindahkan tick sumbu Y ke kanan
ax[1].set_title("5 Kategori Produk dengan Penjualan Terendah (Descending)", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

# Menampilkan grafik
plt.show()


# In[4]:


st.subheader("Customer Detail")
col1, col2 = st.columns(2)
with col1:
    # Menghitung jumlah setiap jenis pembayaran
payment_counts = orders_payments['payment_type'].value_counts()

# Menampilkan persentase setiap jenis pembayaran
payment_percentage = (payment_counts / payment_counts.sum()) * 100
print("Persentase setiap jenis pembayaran:")
print(payment_percentage)

# Membuat pie chart 
plt.figure(figsize=(10, 6))
plt.pie(payment_counts, labels=None, startangle=140, colors=sns.color_palette("Set2"))

# Menambahkan legenda 
plt.legend(
    labels=[f'{count} ({percentage:.1f}%)' for count, percentage in zip(payment_counts, payment_percentage)],
    title="Jenis Pembayaran",
    loc="best"
)

plt.title("Perbandingan Jenis Pembayaran")
plt.axis('equal')  
plt.show()

with col2:
    # Menghitung jumlah setiap status pesanan
order_status_counts = orders_items['order_status'].value_counts()

# Menampilkan persentase setiap status pesanan
order_status_percentage = (order_status_counts / order_status_counts.sum()) * 100
print("Persentase setiap status pesanan:")
print(order_status_percentage)

# Membuat pie chart
plt.figure(figsize=(10, 6))
plt.pie(order_status_counts, labels=None, startangle=140, colors=sns.color_palette("Set2"))

# Menambahkan legenda 
plt.legend(
    labels=[f'{count} ({percentage:.1f}%)' for count, percentage in zip(order_status_counts, order_status_percentage)],
    title="Status Pesanan",
    loc="best"
)

plt.title("Perbandingan Status Pesanan")
plt.axis('equal') 
plt.show()

# Menghitung jumlah pelanggan per kota
customer_city_counts = data_customers['customer_city'].value_counts()

# Mengambil 5 kota teratas 
top_5_cities = customer_city_counts.head(5)
other_cities_count = customer_city_counts[5:].sum()  # Jumlah kota lainnya
top_5_cities['lain-lain'] = other_cities_count  # Menambahkan kategori 'kota lain'

# Menampilkan jumlah pelanggan per kota
print("Jumlah pelanggan per kota:")
print(top_5_cities)

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
plt.show()


# In[ ]:




