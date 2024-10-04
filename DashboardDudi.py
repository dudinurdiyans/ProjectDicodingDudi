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


def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_category_name").product_photos_qty.sum().sort_values(ascending=False).reset_index()
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
sum_order_items_df = create_sum_order_items_df(main_df)
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

# In[3]:


st.subheader("Best & Worst Performing Product")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
 
colors = ["#000000", "#C0C0C0", "#C0C0C0", "#C0C0C0", "#C0C0C0"]
 
sns.barplot(x="product_photos_qty", y="product_category_name", data=total_order_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=30)
ax[0].set_title("Best Sales Product Category", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

# Plot kedua

sns.barplot(x="product_photos_qty", y="product_category_name", data=total_order_items_df.sort_values(by="product_photos_qty", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Sales Product Category", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
 
st.pyplot(fig)

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
    plt.legend(labels=[f'{count} ({percentage:.1f}%)' for count, percentage in zip(payment_counts, payment_percentage)],
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
     plt.legend(labels=[f'{count} ({percentage:.1f}%)' for count, percentage in zip(order_status_counts, order_status_percentage)],
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


st.caption('Copyright (c) Dudee 2024. All rights reserved.')
dataset_df.to_csv("all_data.csv", index=False)
# In[ ]:




