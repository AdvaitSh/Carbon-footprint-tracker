import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import utils
import database
import base64
from io import StringIO

# Page configuration
st.set_page_config(
    page_title="Carbon Footprint Calculator",
    page_icon="🌍",
    layout="wide"
)

# Initialize session state variables
if "calculated" not in st.session_state:
    st.session_state.calculated = False
if "results" not in st.session_state:
    st.session_state.results = {}

# Title and introduction
st.title("🌍 Carbon Footprint Calculator")
st.markdown("**Made by Advait Sharma**")
st.markdown("""
This calculator helps you estimate your carbon footprint based on your lifestyle choices.
Answer a few questions about your transportation, energy usage, and diet to see your environmental impact.
""")

# Create tabs for different sections
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Calculator", "Results", "Recommendations", "About Carbon Footprints", "Saved Footprints"])

with tab1:
    st.header("Calculate Your Carbon Footprint")
    
    # Create form for user inputs
    with st.form("carbon_calculator_form"):
        st.subheader("🚗 Transportation")
        transport_options = {
            "car_petrol": "Petrol/Gasoline Car",
            "car_diesel": "Diesel Car",
            "car_electric": "Electric Vehicle",
            "public_transport": "Public Transport",
            "motorcycle": "Motorcycle"
        }
        transport_type = st.selectbox(
            "What is your primary mode of transportation?",
            options=list(transport_options.keys()),
            format_func=lambda x: transport_options[x]
        )
        
        weekly_distance = st.number_input(
            "How many kilometers do you travel per week?",
            min_value=0.0,
            step=5.0,
            help="Include your regular commute and other routine travel."
        )
        
        st.markdown("---")
        
        st.subheader("✈️ Air Travel")
        short_flights = st.number_input(
            "How many short-haul flights (under 3 hours) do you take per year?",
            min_value=0,
            step=1
        )
        long_flights = st.number_input(
            "How many long-haul flights (over 3 hours) do you take per year?",
            min_value=0,
            step=1
        )
        
        # Assuming average distances for flights
        short_flight_distance = 1000  # km for short-haul flight
        long_flight_distance = 6000   # km for long-haul flight
        
        st.markdown("---")
        
        st.subheader("💡 Household Energy")
        electricity_kwh = st.number_input(
            "How many kilowatt-hours (kWh) of electricity do you use per week?",
            min_value=0.0,
            step=10.0,
            help="Check your electricity bill or use 30-50 kWh for a small apartment, 100-150 kWh for a family home."
        )
        
        gas_kwh = st.number_input(
            "How many kilowatt-hours (kWh) of natural gas do you use per week?",
            min_value=0.0,
            step=10.0,
            help="Check your gas bill or use 0 if you don't use natural gas."
        )
        
        st.markdown("---")
        
        st.subheader("🍽️ Diet")
        diet_options = {
            "meat_beef": "Beef meals",
            "meat_pork": "Pork meals",
            "meat_chicken": "Chicken meals",
            "vegetarian": "Vegetarian meals",
            "vegan": "Vegan meals"
        }
        
        st.write("How many of the following meals do you eat per week?")
        diet_inputs = {}
        for diet_key, diet_label in diet_options.items():
            diet_inputs[diet_key] = st.number_input(
                f"{diet_label}",
                min_value=0,
                max_value=21,
                step=1
            )
            
        st.markdown("---")
        
        st.subheader("🌎 Country")
        country = st.selectbox(
            "Select your country for comparison with national average:",
            options=list(utils.NATIONAL_AVERAGES.keys())
        )
        
        # Submit button
        submitted = st.form_submit_button("Calculate My Footprint")
        
        if submitted:
            # Calculate emissions from transportation
            transport_emissions = utils.calculate_transportation_emissions(transport_type, weekly_distance)
            
            # Calculate emissions from flights (convert to weekly)
            flight_short_emissions = (short_flights * short_flight_distance * utils.EMISSION_FACTORS["flight_short"]) / 52
            flight_long_emissions = (long_flights * long_flight_distance * utils.EMISSION_FACTORS["flight_long"]) / 52
            
            # Calculate emissions from household energy
            household_emissions = utils.calculate_household_emissions(electricity_kwh, gas_kwh)
            
            # Calculate emissions from diet
            diet_emissions = {}
            for diet_type, meals in diet_inputs.items():
                diet_emissions[diet_type] = utils.calculate_food_emissions(diet_type, meals)
            
            total_diet_emissions = sum(diet_emissions.values())
            
            # Calculate weekly and annual totals
            weekly_total = (
                transport_emissions + 
                flight_short_emissions + 
                flight_long_emissions + 
                household_emissions + 
                total_diet_emissions
            )
            annual_total = weekly_total * 52
            
            # Prepare breakdown of emissions
            weekly_breakdown = {
                "Transportation": transport_emissions,
                "Short Flights": flight_short_emissions,
                "Long Flights": flight_long_emissions,
                "Household Energy": household_emissions,
                "Diet": total_diet_emissions
            }
            
            # Get detailed data for recommendations
            detailed_emissions = {
                transport_type: transport_emissions,
                "flight_short": flight_short_emissions,
                "flight_long": flight_long_emissions,
                "electricity": electricity_kwh * utils.EMISSION_FACTORS["electricity"],
                "natural_gas": gas_kwh * utils.EMISSION_FACTORS["natural_gas"],
                **diet_emissions
            }
            
            # Get comparison with national average
            comparison = utils.get_footprint_comparison(annual_total, country)
            
            # Get recommendations
            recommendations = utils.get_recommendations(detailed_emissions)
            
            # Store results in session state
            st.session_state.results = {
                "weekly_total": weekly_total,
                "annual_total": annual_total,
                "weekly_breakdown": weekly_breakdown,
                "comparison": comparison,
                "recommendations": recommendations,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            st.session_state.calculated = True
            
            # Success message and redirect to results tab
            st.success("Your carbon footprint has been calculated! Check the Results tab.")

with tab2:
    st.header("Your Carbon Footprint Results")
    
    if st.session_state.calculated:
        results = st.session_state.results
        
        # Display summary
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Weekly Carbon Footprint")
            st.metric(
                "Carbon Dioxide (CO₂) Emissions",
                f"{results['weekly_total']:.2f} kg"
            )
            
        with col2:
            st.subheader("Annual Carbon Footprint")
            st.metric(
                "Carbon Dioxide (CO₂) Emissions",
                f"{results['annual_total']:.2f} kg"
            )
        
        st.markdown("---")
        
        # Display comparison with national average
        comparison = results["comparison"]
        st.subheader(f"Comparison with {comparison['country']} Average")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                f"{comparison['country']} Average Annual Emissions",
                f"{comparison['national_avg']:.0f} kg CO₂"
            )
            
            percentage_diff = comparison['percentage'] - 100
            arrow = "↑" if percentage_diff > 0 else "↓"
            st.metric(
                "Your Footprint Compared to National Average",
                f"{comparison['percentage']:.1f}%",
                f"{arrow} {abs(percentage_diff):.1f}%",
                delta_color="inverse"
            )
            
            st.info(comparison["message"])
            
        with col2:
            # Create gauge chart for comparison
            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = results['annual_total'],
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Your Annual Footprint (kg CO₂)"},
                gauge = {
                    'axis': {'range': [None, max(comparison['national_avg'] * 2, results['annual_total'] * 1.2)]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, comparison['national_avg'] * 0.5], 'color': "lightgreen"},
                        {'range': [comparison['national_avg'] * 0.5, comparison['national_avg'] * 0.8], 'color': "green"},
                        {'range': [comparison['national_avg'] * 0.8, comparison['national_avg'] * 1.2], 'color': "yellow"},
                        {'range': [comparison['national_avg'] * 1.2, comparison['national_avg'] * 2], 'color': "orange"},
                        {'range': [comparison['national_avg'] * 2, comparison['national_avg'] * 3], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': comparison['national_avg']
                    }
                },
                delta = {'reference': comparison['national_avg'], 'relative': True}
            ))
            
            fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Display breakdown of emissions
        st.subheader("Breakdown of Your Carbon Footprint")
        
        # Prepare data for pie chart
        breakdown_data = pd.DataFrame({
            'Category': list(results["weekly_breakdown"].keys()),
            'Emissions (kg CO₂)': list(results["weekly_breakdown"].values())
        })
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Create pie chart
            fig = px.pie(
                breakdown_data,
                values='Emissions (kg CO₂)',
                names='Category',
                title='Weekly Carbon Footprint by Category',
                color_discrete_sequence=px.colors.sequential.Viridis
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(margin=dict(t=40, b=0, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            # Display breakdown table
            st.dataframe(
                breakdown_data.sort_values(by='Emissions (kg CO₂)', ascending=False),
                use_container_width=True,
                hide_index=True
            )
            
            # Calculate emissions per day
            daily_emissions = results['weekly_total'] / 7
            st.metric("Average Daily Emissions", f"{daily_emissions:.2f} kg CO₂")
        
        st.markdown("---")
        
        # Option to download results as CSV
        st.subheader("Download Your Results")
        
        emissions_df = utils.format_emissions_for_download(results)
        
        csv = emissions_df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        download_filename = f"carbon_footprint_{datetime.now().strftime('%Y%m%d')}.csv"
        href = f'<a href="data:file/csv;base64,{b64}" download="{download_filename}">Download CSV File</a>'
        st.markdown(href, unsafe_allow_html=True)
        
        # Add option to save results to database
        st.markdown("---")
        st.subheader("Save Your Results")
        
        with st.form("save_footprint_form"):
            user_name = st.text_input("Your Name")
            email = st.text_input("Your Email")
            
            save_submitted = st.form_submit_button("Save My Footprint")
            
            if save_submitted:
                if user_name and email:
                    try:
                        footprint_id = database.save_footprint(user_name, email, results)
                        st.success(f"Your footprint has been saved successfully! (ID: {footprint_id})")
                        st.info("You can view your saved footprints in the 'Saved Footprints' tab.")
                    except Exception as e:
                        st.error(f"An error occurred while saving your footprint: {str(e)}")
                else:
                    st.warning("Please provide both your name and email to save your footprint.")
        
    else:
        st.info("Please complete the calculator form in the Calculator tab to see your results.")

with tab3:
    st.header("Personalized Recommendations")
    
    if st.session_state.calculated:
        results = st.session_state.results
        
        st.subheader("Ways to Reduce Your Carbon Footprint")
        
        for i, recommendation in enumerate(results["recommendations"]):
            st.markdown(f"**{i+1}. {recommendation}**")
        
        st.markdown("---")
        
        st.subheader("Small Steps, Big Impact")
        st.markdown("""
        Even small changes can make a significant difference when it comes to your carbon footprint:
        
        * **Transportation:** Each gallon of gasoline burned produces about 8.9 kg of CO₂
        * **Electricity:** LED bulbs use 75% less energy than incandescent bulbs
        * **Diet:** A plant-based meal can save up to 2.5 kg of CO₂ compared to a beef meal
        * **Home:** Turning your thermostat down by 1°C can reduce your heating bill by up to 10%
        """)
        
    else:
        st.info("Please complete the calculator form in the Calculator tab to get personalized recommendations.")

with tab4:
    st.header("About Carbon Footprints")
    
    st.subheader("What is a Carbon Footprint?")
    st.markdown("""
    A carbon footprint is the total amount of greenhouse gases (primarily carbon dioxide) 
    that are generated by our actions. The average carbon footprint for a person in the 
    United States is 16 tonnes, one of the highest rates in the world.
    """)
    
    st.subheader("Main Sources of Carbon Emissions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Transportation:**
        * Car travel
        * Air travel
        * Public transportation
        
        **Home Energy Use:**
        * Electricity consumption
        * Heating and cooling
        * Appliances and devices
        """)
    
    with col2:
        st.markdown("""
        **Food:**
        * Meat consumption (especially beef)
        * Food waste
        * Food transportation
        
        **Consumer Goods:**
        * Manufacturing of products
        * Packaging
        * Waste disposal
        """)
    
    st.subheader("Why Measuring Your Carbon Footprint Matters")
    st.markdown("""
    Understanding your carbon footprint helps you:
    1. Identify the biggest sources of your personal emissions
    2. Make informed choices about where to focus your reduction efforts
    3. Track progress as you make lifestyle changes
    4. Set meaningful goals for reducing your environmental impact
    
    By making small changes in your daily habits, you can significantly reduce your carbon 
    footprint and help combat climate change.
    """)
    
    st.subheader("Global Context")
    st.markdown("""
    To limit global warming to 1.5°C above pre-industrial levels (the goal of the Paris Agreement), 
    the average global carbon footprint per person needs to drop to under 2 tonnes by 2050.
    """)
    
    # Create bar chart of national averages
    national_data = pd.DataFrame({
        'Country': list(utils.NATIONAL_AVERAGES.keys()),
        'Annual CO₂ Emissions Per Person (kg)': list(utils.NATIONAL_AVERAGES.values())
    })
    
    fig = px.bar(
        national_data,
        x='Country',
        y='Annual CO₂ Emissions Per Person (kg)',
        title='Average Annual Carbon Footprint by Country',
        color='Annual CO₂ Emissions Per Person (kg)',
        color_continuous_scale=px.colors.sequential.Viridis
    )
    fig.update_layout(xaxis_title="Country", yaxis_title="kg CO₂ per person")
    
    st.plotly_chart(fig, use_container_width=True)

# Tab 5: Saved Footprints
with tab5:
    st.header("Saved Carbon Footprints")
    st.write("View and manage your previously saved carbon footprint calculations.")
    
    # Option to search by email
    with st.expander("Search by Email", expanded=True):
        search_email = st.text_input("Enter your email to find your saved footprints")
        search_button = st.button("Search")
        
        if search_button and search_email:
            try:
                footprints = database.get_footprints_by_email(search_email)
                if footprints:
                    st.success(f"Found {len(footprints)} saved footprints for {search_email}")
                    
                    # Convert to DataFrame for display
                    df = pd.DataFrame(footprints)
                    df = df[['id', 'user_name', 'weekly_total', 'annual_total', 'country', 'timestamp']]
                    df.columns = ['ID', 'Name', 'Weekly (kg CO₂)', 'Annual (kg CO₂)', 'Country', 'Date Saved']
                    
                    st.dataframe(df, use_container_width=True)
                    
                    # Option to view details of a specific footprint
                    selected_id = st.selectbox("Select a footprint to view details:", 
                                              options=[f["id"] for f in footprints],
                                              format_func=lambda x: f"ID: {x} - {next((f['timestamp'] for f in footprints if f['id'] == x), '')}")
                    
                    if selected_id:
                        footprint = next((f for f in footprints if f["id"] == selected_id), None)
                        if footprint:
                            st.subheader(f"Footprint Details for {footprint['user_name']}")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Weekly Total", f"{footprint['weekly_total']:.2f} kg CO₂")
                                st.metric("Transport Emissions", f"{footprint['transport_emissions']:.2f} kg CO₂")
                                st.metric("Household Emissions", f"{footprint['household_emissions']:.2f} kg CO₂")
                            
                            with col2:
                                st.metric("Annual Total", f"{footprint['annual_total']:.2f} kg CO₂")
                                st.metric("Flight Emissions", f"{footprint['short_flights_emissions'] + footprint['long_flights_emissions']:.2f} kg CO₂")
                                st.metric("Diet Emissions", f"{footprint['diet_emissions']:.2f} kg CO₂")
                            
                            # Create pie chart of emissions breakdown
                            breakdown_data = {
                                "Transportation": footprint['transport_emissions'],
                                "Short Flights": footprint['short_flights_emissions'],
                                "Long Flights": footprint['long_flights_emissions'],
                                "Household Energy": footprint['household_emissions'],
                                "Diet": footprint['diet_emissions']
                            }
                            
                            fig_data = pd.DataFrame({
                                'Category': list(breakdown_data.keys()),
                                'Emissions (kg CO₂)': list(breakdown_data.values())
                            })
                            
                            fig = px.pie(
                                fig_data,
                                values='Emissions (kg CO₂)',
                                names='Category',
                                title='Weekly Carbon Footprint by Category',
                                color_discrete_sequence=px.colors.sequential.Viridis
                            )
                            fig.update_traces(textposition='inside', textinfo='percent+label')
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Delete option
                            if st.button(f"Delete Footprint ID: {selected_id}"):
                                if database.delete_footprint(selected_id):
                                    st.success("Footprint deleted successfully!")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete footprint.")
                else:
                    st.info(f"No saved footprints found for {search_email}.")
            except Exception as e:
                st.error(f"An error occurred while searching for footprints: {str(e)}")
    
    # Show all saved footprints
    with st.expander("View All Saved Footprints"):
        try:
            all_footprints = database.get_all_footprints()
            if all_footprints:
                st.write(f"Total saved footprints: {len(all_footprints)}")
                
                # Convert to DataFrame for display
                all_df = pd.DataFrame(all_footprints)
                all_df = all_df[['id', 'user_name', 'email', 'weekly_total', 'annual_total', 'country', 'timestamp']]
                all_df.columns = ['ID', 'Name', 'Email', 'Weekly (kg CO₂)', 'Annual (kg CO₂)', 'Country', 'Date Saved']
                
                st.dataframe(all_df, use_container_width=True)
                
                # Analytics on all footprints
                if len(all_footprints) > 1:
                    st.subheader("Footprint Analytics")
                    
                    avg_annual = sum(f['annual_total'] for f in all_footprints) / len(all_footprints)
                    min_annual = min(f['annual_total'] for f in all_footprints)
                    max_annual = max(f['annual_total'] for f in all_footprints)
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Average Annual Footprint", f"{avg_annual:.2f} kg CO₂")
                    col2.metric("Minimum Annual Footprint", f"{min_annual:.2f} kg CO₂")
                    col3.metric("Maximum Annual Footprint", f"{max_annual:.2f} kg CO₂")
                    
                    # Time series of saved footprints
                    if len(all_footprints) > 2:
                        st.subheader("Footprints Over Time")
                        time_df = pd.DataFrame(all_footprints)
                        time_df['timestamp'] = pd.to_datetime(time_df['timestamp'])
                        time_df = time_df.sort_values('timestamp')
                        
                        fig = px.line(
                            time_df, 
                            x='timestamp', 
                            y='annual_total',
                            color='user_name',
                            title='Annual Footprints Over Time',
                            labels={'timestamp': 'Date', 'annual_total': 'Annual Footprint (kg CO₂)', 'user_name': 'User'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No footprints have been saved yet.")
        except Exception as e:
            st.error(f"An error occurred while loading all footprints: {str(e)}")

# Footer
st.markdown("---")
st.markdown("### 🌍 Carbon Footprint Calculator")
st.markdown("Helping you understand and reduce your environmental impact.")
st.markdown("Data sources: Various international environmental agencies and research publications.")