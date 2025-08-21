import streamlit as st
import pandas as pd
import os

# Function to load data from CSV files
@st.cache_data
def load_data():
    data_dir = "MultipleFiles"
    claims_df = pd.read_csv(os.path.join(data_dir, "claims_data.csv"))
    food_listings_df = pd.read_csv(os.path.join(data_dir, "food_listings_data.csv"))
    receivers_df = pd.read_csv(os.path.join(data_dir, "receivers_data.csv"))
    providers_df = pd.read_csv(os.path.join(data_dir, "providers_data.csv"))
    return claims_df, food_listings_df, receivers_df, providers_df

claims_df, food_listings_df, receivers_df, providers_df = load_data()

st.set_page_config(layout="wide", page_title="Food Donation & Claims Dashboard")

st.title("🍽️ Food Donation & Claims Analysis")
st.markdown("Explore trends in food donations, claims, and provider/receiver activities.")

# --- Sidebar Navigation ---
st.sidebar.header("Navigation")
section = st.sidebar.radio(
    "Go to",
    [
        "Food Providers & Receivers",
        "Food Listings & Availability",
        "Claims & Distribution",
        "Analysis & Insights",
    ],
)

# --- Section: Food Providers & Receivers ---
if section == "Food Providers & Receivers":
    st.header("Food Providers & Receivers Overview")

    st.subheader("Number of Food Providers and Receivers in Each City")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### Providers per City")
        providers_per_city = providers_df.groupby('City').size().reset_index(name='NumberOfProviders').sort_values('NumberOfProviders', ascending=False)
        st.dataframe(providers_per_city)
    with col2:
        st.markdown("##### Receivers per City")
        receivers_per_city = receivers_df.groupby('City').size().reset_index(name='NumberOfReceivers').sort_values('NumberOfReceivers', ascending=False)
        st.dataframe(receivers_per_city)

    st.subheader("Provider Type Contributing the Most Food")
    provider_food_contribution = food_listings_df.merge(providers_df, on='Provider_ID')
    most_contributing_type = provider_food_contribution.groupby('Type')['Quantity'].sum().reset_index(name='TotalFoodQuantity').sort_values('TotalFoodQuantity', ascending=False)
    st.dataframe(most_contributing_type)
    st.write(f"The provider type contributing the most food is **{most_contributing_type.iloc[0]['Type']}** with **{most_contributing_type.iloc[0]['TotalFoodQuantity']}** units.")

    st.subheader("Contact Information of Food Providers in a Specific City")
    selected_city = st.selectbox("Select a city to view provider contact info:", providers_df['City'].unique())
    city_providers_contact = providers_df[providers_df['City'] == selected_city][['Name', 'Contact', 'Address']]
    st.dataframe(city_providers_contact)

    st.subheader("Receivers Who Have Claimed the Most Food")
    completed_claims = claims_df[claims_df['Status'] == 'Completed']
    claimed_food_details = completed_claims.merge(food_listings_df, on='Food_ID')
    receiver_claimed_food = claimed_food_details.merge(receivers_df, on='Receiver_ID')
    most_claiming_receivers = receiver_claimed_food.groupby('Name_y')['Quantity'].sum().reset_index(name='TotalFoodClaimed').sort_values('TotalFoodClaimed', ascending=False)
    st.dataframe(most_claiming_receivers.rename(columns={'Name_y': 'ReceiverName'}))
    st.write(f"The receiver who has claimed the most food is **{most_claiming_receivers.iloc[0]['ReceiverName']}** with **{most_claiming_receivers.iloc[0]['TotalFoodClaimed']}** units.")


# --- Section: Food Listings & Availability ---
elif section == "Food Listings & Availability":
    st.header("Food Listings & Availability Insights")

    st.subheader("Total Quantity of Food Available from All Providers")
    total_available_food = food_listings_df['Quantity'].sum()
    st.metric("Total Food Available", f"{total_available_food} units")

    st.subheader("City with the Highest Number of Food Listings")
    food_listings_with_city = food_listings_df.merge(providers_df, on='Provider_ID')
    city_with_most_listings = food_listings_with_city.groupby('City')['Food_ID'].count().reset_index(name='NumberOfFoodListings').sort_values('NumberOfFoodListings', ascending=False)
    st.dataframe(city_with_most_most_listings)
    st.write(f"The city with the highest number of food listings is **{city_with_most_listings.iloc[0]['City']}** with **{city_with_most_listings.iloc[0]['NumberOfFoodListings']}** listings.")

    st.subheader("Most Commonly Available Food Types")
    most_common_food_types = food_listings_df.groupby('Food_Type').size().reset_index(name='NumberOfListings').sort_values('NumberOfListings', ascending=False)
    st.dataframe(most_common_food_types)
    st.write(f"The most commonly available food type is **{most_common_food_types.iloc[0]['Food_Type']}** with **{most_common_food_types.iloc[0]['NumberOfListings']}** listings.")


# --- Section: Claims & Distribution ---
elif section == "Claims & Distribution":
    st.header("Claims & Distribution Analysis")

    st.subheader("Number of Food Claims Made for Each Food Item")
    claims_per_food_item = claims_df.merge(food_listings_df, on='Food_ID')
    food_item_claims_count = claims_per_food_item.groupby('Food_Name')['Claim_ID'].count().reset_index(name='NumberOfClaims').sort_values('NumberOfClaims', ascending=False)
    st.dataframe(food_item_claims_count)

    st.subheader("Provider with the Highest Number of Successful Food Claims")
    successful_claims_details = claims_df[claims_df['Status'] == 'Completed'].merge(food_listings_df, on='Food_ID').merge(providers_df, on='Provider_ID')
    provider_successful_claims = successful_claims_details.groupby('Name_y')['Claim_ID'].count().reset_index(name='NumberOfSuccessfulClaims').sort_values('NumberOfSuccessfulClaims', ascending=False)
    st.dataframe(provider_successful_claims.rename(columns={'Name_y': 'ProviderName'}))
    st.write(f"The provider with the highest number of successful food claims is **{provider_successful_claims.iloc[0]['ProviderName']}** with **{provider_successful_claims.iloc[0]['NumberOfSuccessfulClaims']}** successful claims.")

    st.subheader("Percentage of Food Claims by Status")
    claim_status_counts = claims_df['Status'].value_counts().reset_index(name='NumberOfClaims')
    claim_status_counts['Percentage'] = (claim_status_counts['NumberOfClaims'] / len(claims_df)) * 100
    st.dataframe(claim_status_counts)


# --- Section: Analysis & Insights ---
elif section == "Analysis & Insights":
    st.header("Deeper Analysis & Insights")

    st.subheader("Average Quantity of Food Claimed Per Receiver")
    completed_claims_analysis = claims_df[claims_df['Status'] == 'Completed'].merge(food_listings_df, on='Food_ID').merge(receivers_df, on='Receiver_ID')
    avg_quantity_per_receiver = completed_claims_analysis.groupby('Name_y')['Quantity'].mean().reset_index(name='AverageQuantityClaimed').sort_values('AverageQuantityClaimed', ascending=False)
    st.dataframe(avg_quantity_per_receiver.rename(columns={'Name_y': 'ReceiverName'}))

    st.subheader("Most Claimed Meal Type")
    claimed_meal_types = claims_df[claims_df['Status'] == 'Completed'].merge(food_listings_df, on='Food_ID')
    most_claimed_meal_type = claimed_meal_types.groupby('Meal_Type')['Claim_ID'].count().reset_index(name='NumberOfClaims').sort_values('NumberOfClaims', ascending=False)
    st.dataframe(most_claimed_meal_type)
    st.write(f"The most claimed meal type is **{most_claimed_meal_type.iloc[0]['Meal_Type']}** with **{most_claimed_meal_type.iloc[0]['NumberOfClaims']}** claims.")

    st.subheader("Total Quantity of Food Donated by Each Provider")
    total_donated_by_provider = food_listings_df.merge(providers_df, on='Provider_ID')
    provider_donations = total_donated_by_provider.groupby('Name_y')['Quantity'].sum().reset_index(name='TotalQuantityDonated').sort_values('TotalQuantityDonated', ascending=False)
    st.dataframe(provider_donations.rename(columns={'Name_y': 'ProviderName'}))

