import streamlit as st
import numpy as np
import tensorflow as tf
import pandas as pd
import pickle
import warnings
warnings.filterwarnings('ignore')

# Load pre-trained model and encoders
model = tf.keras.models.load_model("artifacts/ann_model.h5")

with open("artifacts/label_encoder_gender.pkl", "rb") as file:
    label_encoder_gender = pickle.load(file)

with open("artifacts/onehot_encoder_geography.pkl", "rb") as file:
    onehot_encoder_geography = pickle.load(file)

with open('artifacts/standard_scaler.pkl', "rb") as file:
    scaler = pickle.load(file)

# Set the page title and other configurations
st.set_page_config(
    page_title="Customer Churn Prediction",  # Title of the page
    page_icon="📊",                        # Optionally set an emoji icon for the tab
    layout="centered",                     # 'centered' or 'wide'
    initial_sidebar_state="auto"            # 'auto', 'expanded', or 'collapsed'
)

import streamlit as st

# Streamlit app
st.title("Bank Churn Prediction")

# Info message at the top for general guidance
st.info("Provide customer details in the form and click **Predict Churn** to know the probability of churn. Adjust the sliders and inputs to explore different scenarios.")

# Theme
base = "dark"

# Create a form for input fields
with st.form(key="input_form"):
    st.subheader("Customer Information")

    # Geography input
    geography = st.selectbox('Geography', onehot_encoder_geography.categories_[0])

    # Gender input
    gender = st.selectbox('Gender', label_encoder_gender.classes_)

    # Numerical inputs
    age = st.slider('Age', 18, 92, 30)
    balance = st.number_input('Balance', min_value=0, step=1000, value=50000)
    credit_score = st.number_input('Credit Score', min_value=300, max_value=850, step=10, value=650)
    estimated_salary = st.number_input('Estimated Salary (annual)', min_value=10000, step=1000, value=50000)
    tenure = st.slider('Tenure (in years)', 0, 10, 1)
    num_of_products = st.slider('Number of Products', 1, 4, 2)
    has_cr_card = st.selectbox("Has Credit Card", [0,1])
    is_active_member = st.selectbox("Is Active Member", [0, 1]) 
    
    # Submit button
    submit_button = st.form_submit_button("Predict Churn")

# If form submit - Process input data and make prediction
if submit_button:
    # Display loading spinner while prediction is being processed
    with st.spinner('Making prediction...'):
        # Prepare input data for the model
        input_data = pd.DataFrame({
            'CreditScore': [credit_score], 
            "Gender": [label_encoder_gender.transform([gender])[0]],
            "Age": [age],
            "Tenure": [tenure],
            "Balance": [balance],
            "NumOfProducts": [num_of_products],
            "HasCrCard": [has_cr_card],
            "IsActiveMember": [is_active_member],
            "EstimatedSalary": [estimated_salary]
        })

        # Encoding Geography
        geography_encoder = onehot_encoder_geography.transform([[geography]]).toarray()
        geography_encoder_df = pd.DataFrame(geography_encoder, columns=onehot_encoder_geography.get_feature_names_out(['Geography']))

        # Combining the DataFrames
        input_data = pd.concat([input_data, geography_encoder_df], axis=1)

        # Scaling the input data
        input_data_scaled = scaler.transform(input_data)

        # Model prediction
        prediction = model.predict(input_data_scaled)
        prediction_probability = prediction[0][0]

        # Display probability
        st.write(f"### Churn Probability: {prediction_probability:.2f}")
        
        # Display churn prediction based on threshold
        if prediction_probability > 0.5:
            st.warning("The customer is likely to churn.")
        else:
            st.success("The customer is not likely to churn.")

## Model Explaination Section
st.sidebar.title("About the Model")
st.sidebar.write("""
    This model predicts whether a customer will churn based on their demographic and account information.
    
    **Input Features:**
    - Geography
    - Gender
    - Age
    - Balance
    - Credit Score
    - Estimated Salary
    - Tenure
    - Number of Products
    - Has Credit Card
    - Is Active Member
    
    **Prediction Logic:**
    The model uses a neural network (ANN) trained on historical customer data to predict the likelihood of customer churn. 
    If the predicted churn probability exceeds 50%, the customer is considered likely to churn.
""")

# Display an info message for the user
st.info("Please input the customer's details and click **Predict Churn** to receive the churn prediction probability.")

# Credits at the bottom of the main page
st.markdown("""
    ---
    **Developed by [raphaelhoudouin](https://github.com/raphaelhoudouin).**  
    For inquiries or feedback, feel free to visit the GitHub profile.
""")

