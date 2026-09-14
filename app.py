

import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import numpy as np
from scipy import interpolate
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Ridge, Lasso, LogisticRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
import warnings
warnings.filterwarnings('ignore')
from io import BytesIO

def main():
    st.title("GFLS Automation")
    st.write("## Data Collation")
    st.write("Upload an Excel or CSV file and Choose a Formatting Option")
    
    # File type toggle
    file_type = st.radio(
        "Select File Type:",
        ("Excel", "CSV"),
        horizontal=True
    )
    
    # File uploader based on selection
    if file_type == "CSV":
        uploaded_file = st.file_uploader(
            "Choose a CSV File", 
            type=['csv'],
            help="Upload your CSV file here"
        )
        sheet_name = None  # CSV files don't have sheets
    else:
        uploaded_file = st.file_uploader(
            "Choose an Excel File", 
            type=['xlsx', 'xls'],
            help="Upload your Excel file here"
        )
        
        # Sheet name input for Excel files
        sheet_name = st.text_input(
            "Enter Sheet Name:", 
            value="Sheet1",
            help="Specify which sheet to read from the Excel file"
        )
    
    # Only show formatting options if file is uploaded
    if uploaded_file is not None:
        st.success(f"File '{uploaded_file.name}' uploaded successfully!")
        
        # Show file info
        file_details = {
            "Filename": uploaded_file.name,
            "File size": f"{uploaded_file.size} bytes",
        }
        st.write("**File Details:**")
        st.json(file_details)
        
        # Preview original data
        try:
            if file_type == "CSV":
                preview_df = pd.read_csv(uploaded_file)
                uploaded_file.seek(0)  # Reset file pointer
            else:
                preview_df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
                uploaded_file.seek(0)  # Reset file pointer
            
            st.write("**Original Data Preview:**")
            st.dataframe(preview_df.head())
            
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            return
        
        st.write("---")
        st.write("**Choose a Formatting Option:**")
        if 'format_selected' not in st.session_state:
            st.session_state.format_selected = None
        # Create columns for buttons
        col1, col2, col3, col4 = st.columns(4)
        # Format buttons
        with col1:
            #format1_clicked = st.button("Format 1", help="Same form, different labels")
            # Get column names for Format 1 dropdown options
            available_columns = preview_df.columns.tolist()
            if st.button("Format 1", key="format1"):
                st.session_state.format_selected = 1
        
        with col2:
            #format2_clicked = st.button("Format 2", help="Years in different columns")
            if st.button("Format 2", key="format2"):
                st.session_state.format_selected = 2
        
        with col3:
            #format3_clicked = st.button("Format 3", help="Year in rows, metrics in columns")
            if st.button("Format 3", key="format3"):
                st.session_state.format_selected = 3
        
        with col4:
            #format4_clicked = st.button("Format 4", help="Metric in columns with labelled years")
            if st.button("Format 4", key="format4"):
                st.session_state.format_selected = 4
        df = None
        # Handle Format 1 with column mapping input
        if st.session_state.format_selected == 1:
            st.write("---")
            st.write("**Format 1: Column Mapping Configuration**")
            st.write("Select which columns from your data correspond to each required field:")
            
            # Create input fields for column mapping
            col_left, col_right = st.columns(2)
            
            with col_left:
                country_col = st.selectbox(
                    "Country column:", 
                    options=available_columns,
                    key="country_col",
                    help="Select the column that contains country/nation data"
                )
                metric_col = st.selectbox(
                    "Metric column:", 
                    options=available_columns,
                    key="metric_col",
                    help="Select the column that contains metric/title data"
                )
                source_col = st.selectbox(
                    "Source column:", 
                    options=available_columns,
                    key="source_col",
                    help="Select the column that contains source data"
                )
            
            with col_right:
                year_col = st.selectbox(
                    "Year column:", 
                    options=available_columns,
                    key = "year_col",
                    help="Select the column that contains year/peak year data"
                )
                value_col = st.selectbox(
                    "Value column:", 
                    options=available_columns,
                    key="value_col",
                    help="Select the column that contains value data"
                )
                assumption_col = st.selectbox(
                    "Assumption column:", 
                    options=available_columns,
                    key="assumption_col",
                    help="Select the column that contains assumption data"
                )
            
            # Create column mapping dictionary
            column_mapping = {
                st.session_state.country_col: 'country',
                st.session_state.year_col: 'year',
                st.session_state.metric_col: 'metric',
                st.session_state.value_col: 'value',
                st.session_state.source_col: 'source',
                st.session_state.assumption_col: 'assumption'
            }
            
            # Show the mapping
            st.write("**Column Mapping Preview:**")
            mapping_df = pd.DataFrame([
                {"Original Column": k, "Maps to": v} 
                for k, v in column_mapping.items()
            ])
            st.table(mapping_df)
            
            # Process button for Format 1
            if st.button("Apply Format", type="primary"):
                df = process_format(uploaded_file, sheet_name, 1, column_mapping)
        
        # Handle other formats
        elif st.session_state.format_selected == 2:
            df = process_format(uploaded_file, sheet_name, 2)
        elif st.session_state.format_selected == 3:
            df = process_format(uploaded_file, sheet_name, 3)
        elif st.session_state.format_selected == 4:
            df = process_format(uploaded_file, sheet_name, 4)
        
        if df is None:
            st.info('Please upload and process your data with the selected format to continue.')
            st.stop()


        corrected_df = df

        apply_year_correction = st.checkbox("Apply Year Correction (Optional)", value=False)

        
        if apply_year_correction:
            ref_year = st.number_input("Enter the reference/correct/latest year:",
                                    min_value=1900, max_value=2100, value=2023, step=1)
            corrected_df = year_correction_section(df, peak_year=ref_year)
            st.write("**Returned Data Preview:**")
            st.dataframe(corrected_df.head())
            corrected_df = corrected_df.reset_index()
            st.dataframe(corrected_df.head())
            # Pivot the table as described
            desired_id_cols = ['country', 'source', 'assumption']
            id_vars = [col for col in desired_id_cols if col in corrected_df.columns]

            metric_cols = [col for col in corrected_df.columns if col not in id_vars]
            long_df = corrected_df.melt(
                id_vars=id_vars,
                value_vars=metric_cols,
                var_name='metric',
                value_name='value'
            )
            long_df['year'] = ref_year
            long_df = long_df[['country', 'year', 'metric', 'value', 'source', 'assumption']]
            corrected_df = long_df

            corrected_df = corrected_df.reset_index(drop=True)
            corrected_df = pd.concat([df, corrected_df], ignore_index=True)
            corrected_df = corrected_df.sort_values(by=['country', 'year', 'metric'], ascending=[True, True, True]).reset_index(drop=True)

            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                corrected_df.to_excel(writer, index=False, sheet_name='Formatted_Data')
            
            st.download_button(
                label=f"📥 Download the Updated Dataframe",
                data=output.getvalue(),
                file_name="UpdatedSheet.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.write("No year correction applied.")
            corrected_df = df
        
        
        st.write("Post-correction DataFrame shape:", corrected_df.shape)
        st.write("Post-correction DataFrame columns:", corrected_df.columns)
        st.dataframe(corrected_df.head())
        
        # Regression Analysis Section
        st.markdown("---")
        st.subheader("Regression Analysis & Prediction")

        # If corrected_df is still the long format, you'll need to select a country/metric
        country_options = corrected_df['country'].unique().tolist()
        metric_options = corrected_df['metric'].unique().tolist()

        selected_country = st.selectbox("Select Country", country_options)
        selected_metric = st.selectbox("Select Metric", metric_options)

        # Filtering for selected group
        filtered = corrected_df[(corrected_df['country'] == selected_country) &
                                (corrected_df['metric'] == selected_metric)].sort_values('year')

        years = filtered['year'].values
        values = filtered['value'].values

        if len(years) < 2:
            st.error("Not enough data points for regression analysis.")
        else:
            # Regression method selection
            method = st.selectbox(
                "Select Regression Method",
                ['linear', 'polynomial', 'ridge', 'lasso', 'logistic', 
                'decision_tree', 'random_forest', 'svm', 'neural_network']
            )

            # Custom hyperparameters for relevant methods
            poly_order = 2
            alpha = 1.0
            C = 1.0
            hidden_layer_sizes = (10,)
            if method == 'polynomial':
                poly_order = st.number_input("Polynomial Order", value=2, min_value=2, max_value=5)
            elif method in ['ridge', 'lasso']:
                alpha = st.number_input("Alpha (regularization strength)", value=1.0)
            elif method in ['svm', 'logistic']:
                C = st.number_input("C (Regularization parameter)", value=1.0)
            elif method == 'neural_network':
                hidden_layer = st.text_input("Hidden Layer Sizes (comma sep.)", value="10")
                try:
                    hidden_layer_sizes = tuple(map(int, hidden_layer.split(",")))
                except:
                    st.warning("Invalid hidden layer sizes, using default (10,)")

            target_year = st.number_input("Target Year for Prediction:", min_value=int(years[-1])+1, 
                                        value=int(years[-1])+1, step=1)

            ####
            if corrected_df is not None:
                st.session_state.df = corrected_df
            # At top-level, initialize in session state:
            if 'latest_prediction' not in st.session_state:
                st.session_state.latest_prediction = None
            if 'prediction_added' not in st.session_state:
                st.session_state.prediction_added = False

            # When predicting (inside Predict Value handler):
            if st.button("Predict Value"):
                try:
                    y_pred = regression_analysis(
                        years=years,
                        values=values,
                        target_year=target_year,
                        method=method,
                        poly_order=poly_order,
                        alpha=alpha,
                        C=C,
                        hidden_layer_sizes=hidden_layer_sizes
                    )
                    st.session_state.latest_prediction = {
                        'country': selected_country,
                        'metric': selected_metric,
                        'year': target_year,
                        'value': y_pred
                    }
                    st.session_state.prediction_added = False  # Clear add flag if new prediction
                    st.success(f"Predicted value for {selected_country}, {selected_metric}, {target_year}: **{y_pred:.3f}**")
                except Exception as e:
                    st.error(f"Regression failed: {e}")

            # If a prediction exists, show add button and value:
            if st.session_state.latest_prediction:
                pred = st.session_state.latest_prediction
                if st.button("Add Prediction to Data Table"):
                    new_row = {
                        "country": pred['country'],
                        "year": pred['year'],
                        "metric": pred['metric'],
                        "value": pred['value'],
                        "source": "regression_prediction",
                        "assumption": ""
                    }
                    if 'df' in st.session_state and st.session_state.df is not None:
                        st.session_state.df = pd.concat([
                            st.session_state.df,
                            pd.DataFrame([new_row])
                        ], ignore_index=True)
                        st.session_state.prediction_added = True
                    else:
                        st.warning("No main DataFrame found in session state.")

            # Show success if recently added
            if st.session_state.prediction_added:
                st.success("Predicted value added to the data table!")

            if 'df' in st.session_state and st.session_state.df is not None:
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    st.session_state.df.to_excel(writer, index=False, sheet_name='Formatted_Data')
                output.seek(0)  # Important: reset pointer to start

                st.download_button(
                    label="Download Current Data Table",
                    data=output.getvalue(),
                    file_name="UpdatedSheet.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.info("No data available to download yet.")

        
        st.markdown("---")
        st.subheader("Data Clustering with KNN Classification")
        ref_year = st.number_input("Enter the year to reviewed:",
                                    min_value=1900, max_value=2100, value=2023, step=1)
        corrected_df = st.session_state.df
        pdf = pivot_with_assumptions(corrected_df, ref_year)
        # Reset index before clustering
        pdf.reset_index(inplace=True)

        # Get numeric columns only for clustering
        numeric_columns = pdf.select_dtypes(include=[np.number]).columns.tolist()

        # Remove any non-feature columns that shouldn't be used for clustering
        columns_to_exclude = ['index', 'level_0'] if 'index' in numeric_columns else []
        if 'level_0' in numeric_columns:
            columns_to_exclude.append('level_0')

        clustering_features = [col for col in numeric_columns if col not in columns_to_exclude]

        if len(clustering_features) >= 2:
            # Feature selection only
            selected_features = st.multiselect(
                "Select features for clustering:",
                clustering_features,
                default=clustering_features[:3] if len(clustering_features) >= 3 else clustering_features[:2]
            )
            
            if len(selected_features) >= 2:
                # Automatically detect country column
                country_col = None
                possible_country_cols = ['country', 'Country', 'COUNTRY', 'entity', 'Entity', 'ENTITY']
                for col in possible_country_cols:
                    if col in pdf.columns:
                        country_col = col
                        break
                
                if country_col:
                    st.info(f"📍 Using '{country_col}' column for country labels")
                else:
                    st.warning("⚠️ No country column detected. Proceeding without country labels.")
                
                # Data preparation and filtering
                n_features = len(selected_features)
                original_data = pdf.copy()
                
                if country_col:
                    # Remove rows where country column is missing
                    original_data = original_data.dropna(subset=[country_col])
                
                # Count missing values for each row in selected features
                missing_counts = original_data[selected_features].isna().sum(axis=1)
                
                # Categorize data based on missing values
                complete_data = original_data[missing_counts == 0].copy()  # All columns present
                partial_data = original_data[missing_counts == 1].copy()   # n-1 columns present
                insufficient_data = original_data[missing_counts > 1].copy()  # Less than n-1 columns
                
                # Display data summary
                st.info(f"""
                📊 **Data Summary for {n_features} selected features:**
                - **Complete data (for clustering)**: {len(complete_data)} countries
                - **Partial data (n-1 columns, for KNN)**: {len(partial_data)} countries  
                - **Insufficient data (dropped)**: {len(insufficient_data)} countries
                - **Total**: {len(original_data)} countries
                """)
                
                # Show countries being clustered
                if len(complete_data) > 0 and country_col:
                    with st.expander(f"🎯 Countries Used for Clustering ({len(complete_data)} countries)"):
                        clustered_countries = complete_data[country_col].tolist()
                        st.write(", ".join(clustered_countries))
                
                # Show dropped countries
                if len(insufficient_data) > 0 and country_col:
                    with st.expander(f"🗑️ Countries Dropped (less than {n_features-1} out of {n_features} columns)"):
                        dropped_countries = insufficient_data[country_col].tolist()
                        st.write(", ".join(dropped_countries))
                
                # Show countries kept aside for KNN
                if len(partial_data) > 0 and country_col:
                    with st.expander(f"⏸️ Countries Kept Aside for KNN Classification ({len(partial_data)} countries)"):
                        kept_aside_countries = partial_data[country_col].tolist()
                        st.write(", ".join(kept_aside_countries))
                
                if len(complete_data) >= 3:  # Need at least 3 countries for meaningful clustering
                    # Clustering parameters
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        n_clusters = st.slider("Number of clusters:", 2, min(8, len(complete_data)//2), 3)
                    
                    with col2:
                        max_clusters = st.slider("Max clusters for elbow method:", n_clusters, 10, 6)
                    
                    with col3:
                        show_pca = st.checkbox("Show PCA Analysis", value=len(selected_features) > 2)
                    
                    # Feature weighting (no normalization)
                    st.write("**Feature Weights (raw values, no normalization):**")
                    feature_weights = {}
                    weight_cols = st.columns(len(selected_features))
                    for i, feature in enumerate(selected_features):
                        with weight_cols[i]:
                            feature_weights[feature] = st.number_input(
                                f"{feature}:",
                                min_value=0.0,
                                value=1.0,
                                step=0.1,
                                key=f"weight_{feature}"
                            )
                    
                    # Create columns for both buttons
                    button_col1, button_col2 = st.columns(2)
                    
                    with button_col1:
                        run_clustering = st.button("🔄 Run Clustering Analysis", key="clustering_button")
                    
                    with button_col2:
                        run_knn = st.button("🤖 Run KNN Classification", key="knn_button", disabled=len(partial_data) == 0)
                    
                    # Initialize session state for storing clustering results
                    if 'clustering_results' not in st.session_state:
                        st.session_state.clustering_results = None
                    if 'weighted_data' not in st.session_state:
                        st.session_state.weighted_data = None
                    if 'scaler' not in st.session_state:
                        st.session_state.scaler = None
                    if 'cluster_labels' not in st.session_state:
                        st.session_state.cluster_labels = None
                    
                    # Run clustering analysis
                    if run_clustering:
                        try:
                            from sklearn.preprocessing import StandardScaler
                            from sklearn.cluster import KMeans
                            from sklearn.decomposition import PCA
                            from sklearn.metrics import silhouette_score
                            import matplotlib.pyplot as plt
                            import seaborn as sns
                            
                            with st.spinner("Performing clustering analysis..."):
                                # Prepare clustering data
                                clustering_data = complete_data[selected_features + ([country_col] if country_col else [])].copy()
                                
                                # Standardize the data
                                scaler = StandardScaler()
                                standardized_data = scaler.fit_transform(clustering_data[selected_features])
                                standardized_df = pd.DataFrame(standardized_data, columns=selected_features)
                                
                                # Apply weights (no normalization)
                                for feature in selected_features:
                                    weight = feature_weights.get(feature, 1.0)
                                    standardized_df[feature] = standardized_df[feature] * weight
                                
                                weighted_data = standardized_df.values
                                
                                # Perform K-means clustering
                                kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                                cluster_labels = kmeans.fit_predict(weighted_data)
                                
                                # Add cluster labels to data
                                clustering_data['Cluster'] = cluster_labels
                                
                                # Store results in session state
                                st.session_state.clustering_results = clustering_data
                                st.session_state.weighted_data = weighted_data
                                st.session_state.scaler = scaler
                                st.session_state.cluster_labels = cluster_labels
                                st.session_state.feature_weights = feature_weights
                                st.session_state.selected_features = selected_features
                                
                                st.success("✅ Clustering analysis completed!")
                                
                        except Exception as e:
                            st.error(f"❌ Error during clustering analysis: {str(e)}")
                            st.exception(e)
                    
                    # Display clustering results if available
                    if st.session_state.clustering_results is not None:
                        clustering_data = st.session_state.clustering_results
                        weighted_data = st.session_state.weighted_data
                        scaler = st.session_state.scaler
                        cluster_labels = st.session_state.cluster_labels
                        
                        # Calculate silhouette score
                        from sklearn.metrics import silhouette_score
                        sil_score = silhouette_score(weighted_data, cluster_labels)
                        
                        # Display results
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Silhouette Score", f"{sil_score:.3f}")
                        with col2:
                            st.metric("Countries Clustered", len(clustering_data))
                        with col3:
                            st.metric("Features Used", len(selected_features))
                        
                        # Elbow Method
                        st.subheader("📊 Elbow Method Analysis")
                        K_max = min(max_clusters + 1, len(clustering_data))
                        inertia = []
                        K_range = range(1, K_max + 1)
                        
                        for K in K_range:
                            if K <= len(clustering_data):
                                from sklearn.cluster import KMeans
                                kmeans_temp = KMeans(n_clusters=K, random_state=42, n_init=10)
                                kmeans_temp.fit(weighted_data)
                                inertia.append(kmeans_temp.inertia_)
                        
                        import matplotlib.pyplot as plt
                        fig_elbow, ax = plt.subplots(figsize=(10, 6))
                        ax.plot(K_range[:len(inertia)], inertia, marker='o', linewidth=2, markersize=8)
                        ax.plot(n_clusters, inertia[n_clusters-1], marker='o', markersize=12, 
                            markerfacecolor='red', markeredgecolor='black', markeredgewidth=2)
                        ax.set_title('Elbow Method for Optimal K', fontsize=14)
                        ax.set_xlabel('Number of Clusters (K)', fontsize=12)
                        ax.set_ylabel('Inertia', fontsize=12)
                        ax.grid(True, alpha=0.3)
                        ax.legend(['Inertia', f'Selected K={n_clusters}'], loc='upper right')
                        st.pyplot(fig_elbow)
                        plt.close()
                        
                        # Cluster Visualization
                        st.subheader("📈 Cluster Visualization")
                        
                        if len(selected_features) == 2:
                            # For exactly 2 features: show direct plot only
                            fig, ax = plt.subplots(figsize=(12, 8))
                            
                            scatter = ax.scatter(
                                clustering_data[selected_features[0]], 
                                clustering_data[selected_features[1]], 
                                c=clustering_data['Cluster'], 
                                cmap='viridis', 
                                alpha=0.7, 
                                s=100, 
                                edgecolor='black',
                                linewidth=0.5
                            )
                            
                            if country_col:
                                for i in range(len(clustering_data)):
                                    ax.annotate(
                                        clustering_data[country_col].iloc[i], 
                                        (clustering_data[selected_features[0]].iloc[i], 
                                        clustering_data[selected_features[1]].iloc[i]), 
                                        fontsize=8, alpha=0.8, ha='center'
                                    )
                            
                            ax.set_title(f'Cluster Visualization: {selected_features[0]} vs {selected_features[1]}', fontsize=14)
                            ax.set_xlabel(selected_features[0], fontsize=12)
                            ax.set_ylabel(selected_features[1], fontsize=12)
                            ax.grid(True, alpha=0.3)
                            plt.colorbar(scatter, ax=ax, label='Cluster')
                            
                        else:
                            # For >2 features: show PCA plot only
                            from sklearn.decomposition import PCA
                            pca_vis = PCA(n_components=2)
                            reduced_data = pca_vis.fit_transform(weighted_data)
                            
                            fig, ax = plt.subplots(figsize=(12, 8))
                            
                            scatter = ax.scatter(
                                reduced_data[:, 0], 
                                reduced_data[:, 1], 
                                c=clustering_data['Cluster'], 
                                cmap='viridis', 
                                alpha=0.7, 
                                s=100, 
                                edgecolor='black',
                                linewidth=0.5
                            )
                            
                            if country_col:
                                for i in range(len(clustering_data)):
                                    ax.annotate(
                                        clustering_data[country_col].iloc[i], 
                                        (reduced_data[i, 0], reduced_data[i, 1]), 
                                        fontsize=8, alpha=0.8, ha='center'
                                    )
                            
                            ax.set_title('PCA Cluster Visualization (All Features)', fontsize=14)
                            ax.set_xlabel(f'PC1 ({pca_vis.explained_variance_ratio_[0]:.2%} variance)', fontsize=12)
                            ax.set_ylabel(f'PC2 ({pca_vis.explained_variance_ratio_[1]:.2%} variance)', fontsize=12)
                            ax.grid(True, alpha=0.3)
                            plt.colorbar(scatter, ax=ax, label='Cluster')
                            
                            # PCA Loadings Analysis
                            if show_pca:
                                st.subheader("🎯 PCA Loadings Analysis")
                                loadings = pca_vis.components_.T * np.sqrt(pca_vis.explained_variance_)
                                loadings_df = pd.DataFrame(
                                    loadings,
                                    index=selected_features,
                                    columns=['PC1', 'PC2']
                                )
                                st.dataframe(loadings_df.round(4), use_container_width=True)
                        
                        st.pyplot(fig)
                        plt.close()
                        
                        # Cluster Analysis
                        st.subheader("🌍 Cluster Assignments (Complete Data)")
                        
                        for cluster_id in sorted(clustering_data['Cluster'].unique()):
                            cluster_countries = clustering_data[clustering_data['Cluster'] == cluster_id]
                            
                            with st.expander(f"Cluster {cluster_id} ({len(cluster_countries)} countries)"):
                                # Show countries in this cluster
                                if country_col:
                                    st.write("**Countries:**")
                                    countries_list = cluster_countries[country_col].tolist()
                                    st.write(", ".join(countries_list))
                                
                                # Feature statistics for this cluster
                                st.write("**Feature Statistics:**")
                                cluster_stats = cluster_countries[selected_features].describe().round(3)
                                st.dataframe(cluster_stats, use_container_width=True)
                    
                    # KNN Classification (separate from clustering results)
                    if run_knn and st.session_state.clustering_results is not None:
                        st.subheader("🤖 KNN Classification for Partial Data")
                        
                        # KNN neighbors = number of features
                        k_neighbors = len(selected_features)
                        
                        st.info(f"Using K={k_neighbors} neighbors (equal to number of features: {len(selected_features)})")
                        
                        try:
                            from sklearn.neighbors import KNeighborsClassifier
                            
                            with st.spinner("Running KNN classification..."):
                                # Get stored clustering results
                                weighted_data = st.session_state.weighted_data
                                cluster_labels = st.session_state.cluster_labels
                                scaler = st.session_state.scaler
                                feature_weights = st.session_state.feature_weights
                                selected_features = st.session_state.selected_features
                                
                                # Train KNN on complete data
                                knn = KNeighborsClassifier(n_neighbors=k_neighbors)
                                knn.fit(weighted_data, cluster_labels)
                                
                                # Prepare partial data for classification
                                knn_results = []
                                
                                for idx, row in partial_data.iterrows():
                                    # Find which feature is missing
                                    missing_features = [col for col in selected_features if pd.isna(row[col])]
                                    available_features = [col for col in selected_features if not pd.isna(row[col])]
                                    
                                    # Fill missing values with cluster centroids
                                    for missing_feat in missing_features:
                                        # Use overall mean as a simple imputation strategy
                                        row[missing_feat] = complete_data[missing_feat].mean()
                                    
                                    # Standardize and apply weights
                                    standardized_row = scaler.transform([row[selected_features]])[0]
                                    for i, feature in enumerate(selected_features):
                                        weight = feature_weights.get(feature, 1.0)
                                        standardized_row[i] = standardized_row[i] * weight
                                    
                                    # Predict cluster
                                    predicted_cluster = knn.predict([standardized_row])[0]
                                    prediction_proba = knn.predict_proba([standardized_row])[0]
                                    confidence = max(prediction_proba)
                                    
                                    knn_results.append({
                                        'Country': row[country_col] if country_col else f'Row_{idx}',
                                        'Predicted_Cluster': predicted_cluster,
                                        'Confidence': confidence,
                                        'Missing_Feature': ', '.join(missing_features),
                                        'Available_Features': ', '.join(available_features)
                                    })
                                
                                knn_results_df = pd.DataFrame(knn_results)
                                
                                # Display KNN results
                                st.write(f"**KNN Classification Results ({len(knn_results_df)} countries):**")
                                st.dataframe(knn_results_df, use_container_width=True)
                                
                                # Show KNN results by cluster
                                st.subheader("🔍 KNN Results by Cluster")
                                for cluster_id in sorted(knn_results_df['Predicted_Cluster'].unique()):
                                    cluster_knn = knn_results_df[knn_results_df['Predicted_Cluster'] == cluster_id]
                                    
                                    with st.expander(f"KNN Cluster {cluster_id} ({len(cluster_knn)} countries)"):
                                        if country_col:
                                            countries_knn = cluster_knn['Country'].tolist()
                                            st.write(f"**Countries:** {', '.join(countries_knn)}")
                                        
                                        avg_confidence = cluster_knn['Confidence'].mean()
                                        st.write(f"**Average Confidence:** {avg_confidence:.3f}")
                                        
                                        st.dataframe(cluster_knn[['Country', 'Confidence', 'Missing_Feature']], use_container_width=True)
                                
                                # Store KNN results in session state for download
                                st.session_state.knn_results = knn_results_df
                                
                        except Exception as e:
                            st.error(f"❌ Error during KNN classification: {str(e)}")
                            st.exception(e)
                    
                    elif run_knn and st.session_state.clustering_results is None:
                        st.warning("⚠️ Please run clustering analysis first before KNN classification.")
                    
                    # Download options (always available if clustering is done)
                    if st.session_state.clustering_results is not None:
                        with st.expander("📥 Download Results"):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                # Clustering results
                                clustering_csv = st.session_state.clustering_results.to_csv(index=False)
                                st.download_button(
                                    "📥 Download Clustering Results",
                                    clustering_csv,
                                    "clustering_results.csv",
                                    "text/csv"
                                )
                            
                            with col2:
                                if 'knn_results' in st.session_state and st.session_state.knn_results is not None:
                                    knn_csv = st.session_state.knn_results.to_csv(index=False)
                                    st.download_button(
                                        "📥 Download KNN Results",
                                        knn_csv,
                                        "knn_classification_results.csv",
                                        "text/csv"
                                    )
                            
                            with col3:
                                # Combined results
                                if 'knn_results' in st.session_state and st.session_state.knn_results is not None:
                                    all_results = st.session_state.clustering_results.copy()
                                    all_results['Data_Type'] = 'Complete'
                                    
                                    knn_for_download = partial_data.copy()
                                    knn_for_download['Cluster'] = st.session_state.knn_results['Predicted_Cluster'].values
                                    knn_for_download['Data_Type'] = 'KNN_Classified'
                                    
                                    combined_results = pd.concat([all_results, knn_for_download], ignore_index=True)
                                    combined_csv = combined_results.to_csv(index=False)
                                    st.download_button(
                                        "📥 Download All Results",
                                        combined_csv,
                                        "all_clustering_results.csv",
                                        "text/csv"
                                    )
                
                else:
                    st.warning(f"⚠️ Need at least 3 countries with complete data for clustering. Currently have {len(complete_data)}.")
            
            else:
                st.warning("⚠️ Please select at least 2 features for clustering.")

        else:
            st.warning("⚠️ Not enough numeric columns available for clustering.")




def year_correction_section(df, peak_year=2023):
    st.write("----")
    st.write("## Year Correction")
    
    pdf = pivot_with_assumptions(df, peak_year)
    st.write("### Original Data Sample")
    st.dataframe(df.head(10))

    st.write("### Pivot Table Sample")
    st.dataframe(pdf.head(10))

    missing_by_column = pdf.isnull().sum()
    total_missing = missing_by_column.sum()

    st.write("Missing values by column:")
    st.write(missing_by_column)
    st.write(f"**Total missing values:** {total_missing}")

    # If nothing missing, exit early and return the unmodified pivot
    if total_missing == 0:
        st.success("No missing values found in the pivot table - no interpolation/extrapolation needed!")
        return pdf

    # --- 🌟 New: User choice between interpolation/extrapolation ---
    fix_method = st.radio(
        "Fill method:",
        ["Interpolate", "Extrapolate"],
        help="Choose whether to interpolate (fill between known years) or extrapolate (extend beyond known years)."
    )

    if fix_method == "Interpolate":
        methods = ['linear', 'polynomial', 'spline', 'nearest_neighbour', 'piecewise_constant', 'logarithmic']
        selected_method = st.selectbox("Select interpolation method:", methods)
        interpolate_now = st.checkbox("Run Interpolation", value=False)
        if interpolate_now:
            try:
                original_missing = total_missing
                result = interpolate_col(pdf, df, peak_year=peak_year, columns='None', method=selected_method)
                # -- rest of your code unchanged, see below
            except Exception as e:
                st.error(f"Interpolation failed for {selected_method}: {str(e)}")
                st.exception(e)
                return pdf
        else:
            st.info("Interpolation not run. Returning pivot table as is.")
            return pdf

    elif fix_method == "Extrapolate":
        methods = ['linear', 'polynomial', 'spline', 'nearest_neighbour', 'piecewise_constant', 'logarithmic']
        selected_method = st.selectbox("Select extrapolation method:", methods)
        # Extra: (provide polynomial order & moving average window for advanced users, if needed)
        if selected_method == 'polynomial':
            order = st.number_input("Polynomial order (for extrapolation):", min_value=1, max_value=5, value=2)
        else:
            order = 2  # default value

        ma_window = st.number_input("Moving average window (for extrapolation):", min_value=1, max_value=10, value=3)

        extrapolate_now = st.checkbox("Run Extrapolation", value=False)
        if extrapolate_now:
            try:
                original_missing = total_missing
                # ------- Run extrapolation -------
                result = extrapolate_col(
                    pdf, df,
                    peak_year=peak_year, columns='None', method=selected_method, order=order, ma_window=ma_window
                )
                # -- rest of your code as with interpolation, see below
            except Exception as e:
                st.error(f"Extrapolation failed for {selected_method}: {str(e)}")
                st.exception(e)
                return pdf
        else:
            st.info("Extrapolation not run. Returning pivot table as is.")
            return pdf

    # ---- Shared post-processing, if we have a result ----
    if 'result' in locals() and result is not None:
        final_missing = result.isnull().sum().sum()
        interpolated_values = original_missing - final_missing

        st.write(f"**Original missing:** {original_missing}")
        st.write(f"**Final missing:** {final_missing}")
        st.write(f"**Values filled:** {interpolated_values}")

        if interpolated_values > 0:
            original_nulls = pdf.isnull().sum()
            final_nulls = result.isnull().sum()
            changed_columns = original_nulls - final_nulls
            affected_cols = changed_columns[changed_columns > 0].to_dict()
            st.write("**Columns affected:**")
            st.write(affected_cols)

            st.write("**Sample of filled data:**")
            st.dataframe(result.head(10))
        else:
            st.warning("No values were filled!")

        # Return the filled dataframe  
        return result

    st.error("Unexpected error: No result generated.")
    return pdf

def interpolate_col(pdf, df, peak_year=2023, columns='None', method='linear'):
    """
    Interpolate missing values in the pivot DataFrame `pdf` using the specified method.

    Parameters:
    - pdf: pivot DataFrame with countries as index and metrics as columns (including 'source' and 'assumptions')
    - df: original DataFrame (not used directly here but kept for compatibility)
    - peak_year: year used for filtering or reference (not used here but kept for compatibility)
    - columns: list of columns to interpolate or 'None' to interpolate all numeric columns
    - method: interpolation method as string

    Returns:
    - DataFrame with interpolated values
    """
    # Copy to avoid modifying original
    df_interp = pdf.copy()

    # Select columns to interpolate
    if columns == 'None':
        # Select numeric columns only (exclude 'source' and 'assumptions')
        cols_to_interp = df_interp.select_dtypes(include=[np.number]).columns.tolist()
    else:
        cols_to_interp = columns

    # Define supported methods mapping to pandas interpolate methods or custom
    pandas_methods = ['linear', 'polynomial', 'spline', 'nearest', 'pad', 'ffill', 'bfill']
    # Map your method names to pandas or custom
    method_map = {
        'linear': 'linear',
        'polynomial': 'polynomial',
        'spline': 'spline',
        'nearest_neighbour': 'nearest',
        'piecewise_constant': 'pad',  # forward fill as piecewise constant approx
        'logarithmic': 'logarithmic'  # custom implementation below
    }

    if method not in method_map:
        raise ValueError(f"Interpolation method '{method}' not supported.")

    interp_method = method_map[method]

    # For polynomial and spline, define order
    order = 2

    # Interpolate each column separately
    for col in cols_to_interp:
        series = df_interp[col]

        if series.isnull().all():
            # Skip columns with all NaNs
            continue

        if interp_method == 'logarithmic':
            # Custom logarithmic interpolation:
            # Interpolate on log scale, then exponentiate back
            # Handle zeros or negative values by shifting data if needed
            s = series.copy()
            # Shift to positive if needed
            min_val = s.min()
            shift = 0
            if min_val <= 0:
                shift = abs(min_val) + 1
                s = s + shift

            # Log transform
            s_log = np.log(s)

            # Interpolate on log scale using linear method
            s_log_interp = s_log.interpolate(method='linear', limit_direction='both')

            # Exponentiate back and shift
            s_interp = np.exp(s_log_interp) - shift

            df_interp[col] = s_interp

        elif interp_method in ['polynomial', 'spline']:
            # Use pandas interpolate with order
            try:
                df_interp[col] = series.interpolate(method=interp_method, order=order, limit_direction='both')
            except Exception as e:
                # fallback to linear if polynomial/spline fails
                df_interp[col] = series.interpolate(method='linear', limit_direction='both')

        elif interp_method == 'pad':
            # Piecewise constant: carry the previous value forward, and back-fill
            # leading gaps (interpolate(method='pad') is deprecated in pandas)
            df_interp[col] = series.ffill().bfill()

        else:
            # Use pandas interpolate for other methods
            # Note: pandas interpolate does not support 'nearest_neighbour' but supports 'nearest'
            try:
                df_interp[col] = series.interpolate(method=interp_method, limit_direction='both')
            except Exception as e:
                # fallback to linear if error
                df_interp[col] = series.interpolate(method='linear', limit_direction='both')

    return df_interp

def cagr(start, end, periods):
    """Compound Annual Growth Rate"""
    return (end / start) ** (1 / periods) - 1 if start > 0 and periods > 0 else 0

def extrapolate_col(pdf, df, peak_year=2023, columns='None', method='linear', order=2, ma_window=3):
    """
    Extrapolate missing values in pdf for peak_year, using historical data from df
    Methods: 'cagr', 'linear_regression', 'polynomial_regression', 'moving_average_growth', 'arima'
    """
    import warnings
    warnings.filterwarnings("ignore")
    
    df_extrap = pdf.copy()

    if columns == 'None':
        cols_to_extrap = df_extrap.select_dtypes(include=[np.number]).columns.tolist()
    else:
        cols_to_extrap = columns

    for country in df_extrap.index:
        for col in cols_to_extrap:
            mask = (df['country'] == country) & (df['metric'] == col)
            hist = df[mask].sort_values('year')
            years = hist['year'].values
            values = hist['value'].values

            # Only extrapolate if missing
            if pd.isnull(df_extrap.loc[country, col]) and len(years) >= 2:
                target_year = peak_year

                if method == 'cagr':
                    # Use only first and last actual values
                    start, end = values[0], values[-1]
                    periods = years[-1] - years[0]
                    if start > 0 and periods > 0:
                        growth_rate = cagr(start, end, periods)
                        n_extrap = target_year - years[-1]
                        if n_extrap > 0:
                            y_pred = end * ((1 + growth_rate) ** n_extrap)
                            df_extrap.loc[country, col] = y_pred

                elif method == 'linear_regression':
                    # y = beta0 + beta1 * year
                    beta = np.polyfit(years, values, 1)
                    y_pred = np.polyval(beta, target_year)
                    df_extrap.loc[country, col] = y_pred

                elif method == 'polynomial_regression':
                    deg = order if len(years) > order else 2
                    beta = np.polyfit(years, values, deg)
                    y_pred = np.polyval(beta, target_year)
                    df_extrap.loc[country, col] = y_pred

                elif method == 'moving_average_growth':
                    # Compute yearly growth rates, moving average, then extrapolate
                    if len(values) >= ma_window + 1:
                        growth_rates = values[1:] / values[:-1] - 1
                        avg_growth = pd.Series(growth_rates).rolling(ma_window).mean().iloc[-1]
                        if np.isnan(avg_growth):
                            avg_growth = np.mean(growth_rates)
                        n_extrap = target_year - years[-1]
                        y_pred = values[-1] * ((1 + avg_growth) ** n_extrap)
                        df_extrap.loc[country, col] = y_pred

                elif method == 'arima':
                    try:
                        from statsmodels.tsa.arima.model import ARIMA
                        n_extrap = int(target_year - years[-1])
                        if len(values) > 3 and n_extrap > 0:  # ARIMA needs more data
                            model = ARIMA(values.astype(float), order=(1,1,0))
                            model_fit = model.fit()
                            # statsmodels rejects numpy ints for `steps` and returns
                            # a plain ndarray when fitted on an ndarray
                            forecast = np.asarray(model_fit.forecast(steps=n_extrap))
                            y_pred = float(forecast[-1])
                            df_extrap.loc[country, col] = y_pred
                    except ImportError:
                        # No statsmodels installed
                        pass
                # You can add more methods!
    return df_extrap

def regression_analysis(years, values, target_year, method='linear', poly_order=2, C=1.0, alpha=1.0, hidden_layer_sizes=(10,)):
    # Converts years and values to proper numpy arrays
    X = np.array(years).reshape(-1, 1)
    y = np.array(values)
    X_pred = np.array([[target_year]])

    def perform_linear_regression():
        model = LinearRegression()
        model.fit(X, y)
        return model.predict(X_pred)[0]

    def perform_polynomial_regression():
        from sklearn.preprocessing import PolynomialFeatures
        from sklearn.linear_model import LinearRegression
        pf = PolynomialFeatures(degree=poly_order)
        X_poly = pf.fit_transform(X)
        X_pred_poly = pf.transform(X_pred)
        model = LinearRegression()
        model.fit(X_poly, y)
        return model.predict(X_pred_poly)[0]

    def perform_ridge_regression():
        model = Ridge(alpha=alpha)
        model.fit(X, y)
        return model.predict(X_pred)[0]

    def perform_lasso_regression():
        model = Lasso(alpha=alpha)
        model.fit(X, y)
        return model.predict(X_pred)[0]

    def perform_logistic_regression():
        # For binary response; convert y to labels if necessary
        model = LogisticRegression(C=C)
        y_bin = (y > np.median(y)).astype(int)  # Example binarization
        model.fit(X, y_bin)
        return model.predict(X_pred)[0]

    def perform_decision_tree_regression():
        model = DecisionTreeRegressor()
        model.fit(X, y)
        return model.predict(X_pred)[0]

    def perform_random_forest_regression():
        model = RandomForestRegressor()
        model.fit(X, y)
        return model.predict(X_pred)[0]

    def perform_svm_regression():
        model = SVR(C=C)
        model.fit(X, y)
        return model.predict(X_pred)[0]

    def perform_neural_network_regression():
        model = MLPRegressor(hidden_layer_sizes=hidden_layer_sizes, max_iter=1000)
        model.fit(X, y)
        return model.predict(X_pred)[0]

    method_dispatch = {
        'linear': perform_linear_regression,
        'polynomial': perform_polynomial_regression,
        'ridge': perform_ridge_regression,
        'lasso': perform_lasso_regression,
        'logistic': perform_logistic_regression,
        'decision_tree': perform_decision_tree_regression,
        'random_forest': perform_random_forest_regression,
        'svm': perform_svm_regression,
        'neural_network': perform_neural_network_regression,
    }

    if method not in method_dispatch:
        raise ValueError(f"Unknown regression method: {method}")

    return method_dispatch[method]()

def process_format(uploaded_file, sheet_name, format_num, column_mapping=None):
    """Process the uploaded file with the selected format"""
    
    try:
        # Reset file pointer
        uploaded_file.seek(0)
        
        # Apply the selected format using your existing functions
        if format_num == 1:
            df = df_format1(uploaded_file, sheet_name, column_mapping)
            format_name = "Format 1 - Same form, different labels"
            output_filename = "Testing1.xlsx"
        elif format_num == 2:
            df = df_format2(uploaded_file, sheet_name)
            format_name = "Format 2 - Years in different columns"
            output_filename = "Testing2.xlsx"
        elif format_num == 3:
            df = df_format3(uploaded_file, sheet_name)
            format_name = "Format 3 - Year in rows, metrics in columns"
            output_filename = "Testing3.xlsx"
        elif format_num == 4:
            df = df_format4(uploaded_file, sheet_name)
            format_name = "Format 4 - Metric in columns with labelled years"
            output_filename = "Testing4.xlsx"
        
        # Display results
        st.success(f"✅ {format_name} applied successfully!")
        
        # Show formatted data
        st.write("**Formatted Data:**")
        st.dataframe(df)
        
        # Show data info
        st.write("**Data Info:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rows", df.shape[0])
        with col2:
            st.metric("Columns", df.shape[1])
        with col3:
            st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum()/1024:.2f} KB")
        
        # Create download button
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Formatted_Data')
        
        st.download_button(
            label=f"Download {format_name}",
            data=output.getvalue(),
            file_name=output_filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        return df
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        st.write("Please check your file format and try again.")
#Function that has straight up same values:
def df_format1(file_name, sheet_name='Sheet1', column_mapping=None, header=0, usecols=None, is_excel=True):
    from pandas import read_excel, read_csv
    
    try:
        # Read the data
        if is_excel:
            df = read_excel(file_name, sheet_name=sheet_name, header=header, usecols=usecols)
        else:
            df = read_csv(file_name, header=header, usecols=usecols)
        
        # Apply column mapping if provided
        if column_mapping:
            df = df.rename(columns=column_mapping)
            print(f"Columns renamed using mapping: {column_mapping}")
        
        print(f"Final columns: {list(df.columns)}")
        return df
        
    except Exception as e:
        print(f"Error reading or transforming file: {e}")
        raise

#Function that has different years as columns
def df_format2(file_name, sheet_name='Sheet1', header=0, usecols=None, is_excel=True):
    from pandas import read_excel, read_csv
    
    try:
        # Read the data
        if is_excel:
            df = read_excel(file_name, sheet_name=sheet_name, header=header, usecols=usecols)
        else:
            df = read_csv(file_name, header=header, usecols=usecols)
        
        # Transform to long format using the row-based function
        transformed_df = transform_rows_to_long_format(df)
        
        return transformed_df
        
    except Exception as e:
        print(f"Error reading or transforming file: {e}")
        raise

def transform_rows_to_long_format(df):
    import pandas as pd
    import re
    
    # Debug: Print structure
    print("Column names:", df.columns.tolist())
    print("First 3 rows:")
    print(df.head(3))
    
    # Find country column
    country_col = None
    for col in df.columns:
        if 'country' in str(col).lower():
            country_col = col
            break
    
    if country_col is None:
        print("Available columns:")
        for i, col in enumerate(df.columns):
            print(f"{i}: {col} - Sample values: {df[col].dropna().head(3).tolist()}")
        # Manually specify if needed
        country_col = df.columns[0]  # Change this index if needed
        print(f"Using column: {country_col}")
    
    print(f"Selected country column: {country_col}")
    
    # Find parameter/metric column
    param_col = None
    for col in df.columns:
        if any(keyword in str(col).lower() for keyword in ['parameter', 'metric', 'variable', 'indicator']):
            param_col = col
            break
    
    if param_col is None:
        # Look for a column that seems to contain parameter names
        for col in df.columns:
            if col != country_col and df[col].dtype == 'object':
                sample_values = df[col].dropna().astype(str).head(5)
                if any(len(str(val)) > 5 for val in sample_values):  # Assuming parameter names are longer
                    param_col = col
                    break
    
    if param_col is None:
        print("Available columns for parameters:")
        for i, col in enumerate(df.columns):
            if col != country_col:
                print(f"{i}: {col} - Sample values: {df[col].dropna().head(3).tolist()}")
        param_col = df.columns[1]  # Default to second column
        print(f"Using parameter column: {param_col}")
    
    print(f"Selected parameter column: {param_col}")
    
    # Find year columns (Y1 2021, Y2 2022, etc.)
    year_columns = []
    for col in df.columns:
        if col not in [country_col, param_col]:
            # Extract year from column name
            year_match = re.search(r'(19\d{2}|20\d{2})', str(col))
            if year_match:
                year_columns.append({
                    'column': col,
                    'year': int(year_match.group(1))
                })
    
    print(f"Found year columns: {[(yc['column'], yc['year']) for yc in year_columns]}")
    
    # Create long format data
    long_format_data = []
    
    for _, row in df.iterrows():
        country = row[country_col]
        parameter = row[param_col]
        
        # Skip if country or parameter is null/empty
        if pd.isna(country) or pd.isna(parameter):
            continue
            
        # Skip if parameter is empty string
        if str(parameter).strip() == '':
            continue
        
        # Process each year column
        for year_col_info in year_columns:
            col_name = year_col_info['column']
            year = year_col_info['year']
            value = row[col_name]
            
            # Skip if value is null, empty, or zero
            if pd.isna(value) or value == '' or value == 0:
                continue
                
            # Convert to float if possible
            try:
                value = float(value)
                # Skip if value is zero (after conversion)
                if value == 0:
                    continue
            except (ValueError, TypeError):
                # Keep as string if can't convert to float
                pass
            
            long_row = {
                'country': str(country).strip(),
                'year': year,
                'metric': str(parameter).strip(),
                'value': value,
                'source': 'Original Dataset',
                'assumption': None
            }
            long_format_data.append(long_row)
    
    # Create the final dataframe
    result_df = pd.DataFrame(long_format_data)
    
    print(f"\nOriginal shape: {df.shape}")
    print(f"Long format shape: {result_df.shape}")
    print(f"Countries found: {result_df['country'].nunique()}")
    print(f"Parameters found: {result_df['metric'].nunique()}")
    print(f"Years found: {sorted(result_df['year'].unique())}")
    
    return result_df

#Function that has different metrics as columns and years as rows
def df_format3(file_name, sheet_name='Sheet1', header=0, usecols=None, is_excel=True):
    from pandas import read_excel, read_csv
    
    try:
        # Read the data
        if is_excel:
            df = read_excel(file_name, sheet_name=sheet_name, header=header, usecols=usecols)
        else:
            df = read_csv(file_name, header=header, usecols=usecols)
        
        # Transform to long format using the metrics-as-columns function
        transformed_df = transform_metrics_columns_to_long_format(df)
        
        return transformed_df
        
    except Exception as e:
        print(f"Error reading or transforming file: {e}")
        raise

def transform_metrics_columns_to_long_format(df):
    import pandas as pd
    import re
    
    # Debug: Print structure
    print("Column names:", df.columns.tolist())
    print("First 3 rows:")
    print(df.head(3))
    
    # Find country column
    country_col = None
    for col in df.columns:
        if 'country' in str(col).lower():
            country_col = col
            break
    
    if country_col is None:
        print("Available columns:")
        for i, col in enumerate(df.columns):
            print(f"{i}: {col} - Sample values: {df[col].dropna().head(3).tolist()}")
        country_col = df.columns[0]  # Default to first column
        print(f"Using column: {country_col}")
    
    print(f"Selected country column: {country_col}")
    
    # Find year column
    year_col = None
    for col in df.columns:
        if any(keyword in str(col).lower() for keyword in ['year', 'period', 'date', 'time']):
            year_col = col
            break
    
    if year_col is None:
        # Look for a column that seems to contain years
        for col in df.columns:
            if col != country_col:
                sample_values = df[col].dropna().astype(str).head(5)
                if any(re.search(r'(19\d{2}|20\d{2})', str(val)) for val in sample_values):
                    year_col = col
                    break
    
    if year_col is None:
        print("Available columns for years:")
        for i, col in enumerate(df.columns):
            if col != country_col:
                print(f"{i}: {col} - Sample values: {df[col].dropna().head(3).tolist()}")
        year_col = df.columns[1]  # Default to second column
        print(f"Using year column: {year_col}")
    
    print(f"Selected year column: {year_col}")
    
    # Find metric columns (everything except country and year)
    metric_columns = []
    for col in df.columns:
        if col not in [country_col, year_col]:
            metric_columns.append(col)
    
    print(f"Found metric columns: {metric_columns}")
    
    # Create long format data
    long_format_data = []
    
    for _, row in df.iterrows():
        country = row[country_col]
        year_value = row[year_col]
        
        # Skip if country or year is null/empty
        if pd.isna(country) or pd.isna(year_value):
            continue
            
        # Skip if country is empty string
        if str(country).strip() == '':
            continue
        
        # Extract year from year_value if it's not already a clean year
        if isinstance(year_value, str):
            year_match = re.search(r'(19\d{2}|20\d{2})', str(year_value))
            if year_match:
                year = int(year_match.group(1))
            else:
                try:
                    year = int(year_value)
                except ValueError:
                    continue
        else:
            try:
                year = int(year_value)
            except (ValueError, TypeError):
                continue
        
        # Process each metric column
        for metric_col in metric_columns:
            value = row[metric_col]
            
            # Skip if value is null, empty, or zero
            if pd.isna(value) or value == '' or value == 0:
                continue
                
            # Convert to float if possible
            try:
                value = float(value)
                # Skip if value is zero (after conversion)
                if value == 0:
                    continue
            except (ValueError, TypeError):
                # Keep as string if can't convert to float
                pass
            
            long_row = {
                'country': str(country).strip(),
                'year': year,
                'metric': str(metric_col).strip(),
                'value': value,
                'source': 'Original Dataset',
                'assumption': None
            }
            long_format_data.append(long_row)
    
    # Create the final dataframe
    result_df = pd.DataFrame(long_format_data)
    
    print(f"\nOriginal shape: {df.shape}")
    print(f"Long format shape: {result_df.shape}")
    print(f"Countries found: {result_df['country'].nunique()}")
    print(f"Metrics found: {result_df['metric'].nunique()}")
    print(f"Years found: {sorted(result_df['year'].unique())}")
    
    return result_df

#Function that has parameters in cols with labels having the year
def df_format4(file_name, sheet_name='Sheet1', header=0, usecols=None, is_excel=True):
    from pandas import read_excel, read_csv
    
    try:
        # Read the data
        if is_excel:
            df = read_excel(file_name, sheet_name=sheet_name, header=header, usecols=usecols)
        else:
            df = read_csv(file_name, header=header, usecols=usecols)
        
        # Transform to long format
        transformed_df = transform_cols_to_long_format(df)
        
        return transformed_df
        
    except Exception as e:
        print(f"Error reading or transforming file: {e}")
        raise

def transform_cols_to_long_format(df):
    import pandas as pd
    import re
    
    # Debug: Print column names and first few rows
    print("Column names:", df.columns.tolist())
    print("First 3 rows:")
    print(df.head(3))
    
    # Extract years from column names
    years = []
    for col in df.columns:
        year_matches = re.findall(r'(19\d{2}|20\d{2})', str(col))
        years.extend([int(year) for year in year_matches])
    
    unique_years = sorted(list(set(years)))
    print(f"Found years: {unique_years}")
    
    # Create an empty list to store all rows
    long_format_data = []
    
    # IMPROVED COUNTRY COLUMN DETECTION
    country_col = None
    
    # Method 1: Look for column with 'country' in name
    for col in df.columns:
        if 'country' in str(col).lower():
            country_col = col
            break
    
    # Method 2: If no 'country' column, look for columns with country-like values
    if country_col is None:
        for col in df.columns:
            # Check if this column contains country-like strings
            sample_values = df[col].dropna().astype(str).head(10)
            if any(len(str(val)) > 2 and str(val).isalpha() for val in sample_values):
                country_col = col
                break
    
    # Method 3: Let user specify or use a specific column index
    if country_col is None:
        print("Available columns:")
        for i, col in enumerate(df.columns):
            print(f"{i}: {col} - Sample values: {df[col].dropna().head(3).tolist()}")
        
        # You can manually specify the column here
        country_col = df.columns[0]  # Change this index if needed
        print(f"Using column: {country_col}")
    
    print(f"Selected country column: {country_col}")
    print(f"Sample country values: {df[country_col].dropna().head(5).tolist()}")
    
    # Define columns to skip (non-metric columns)
    skip_columns = [country_col]
    
    # Add other non-metric columns that should be skipped
    for col in df.columns:
        if any(keyword in str(col).lower() for keyword in ['country', 'mapped', 'income', 'level', 'index']):
            skip_columns.append(col)
    
    # Remove duplicates from skip_columns
    skip_columns = list(set(skip_columns))
    
    # Iterate through each row in the dataframe
    for _, row in df.iterrows():
        country = row[country_col]
        
        # Skip if country is NaN or empty
        if pd.isna(country) or str(country).strip() == '':
            continue
        
        # Process each metric column
        for col in df.columns:
            if col in skip_columns:
                continue
                
            value = row[col]
            
            # Skip if value is empty, NaN, or whitespace
            if pd.isna(value) or str(value).strip() == '':
                continue
            
            # Clean the value
            if isinstance(value, str):
                value = value.strip().replace(',', '')
            
            # Try to convert to numeric and check if it's zero
            try:
                numeric_value = float(value)
                # SKIP ZERO VALUES
                if numeric_value == 0:
                    continue
            except (ValueError, TypeError):
                # If can't convert to numeric, keep as string but skip if it's "0"
                if str(value).strip() == "0":
                    continue
            
            # Clean the metric name by removing years
            clean_metric = col
            for year in unique_years:
                clean_metric = clean_metric.replace(f'({year})', '').replace(f'-{year}', '').replace(f' {year}', '')
            clean_metric = clean_metric.strip()
            
            # Extract years from THIS specific column
            column_years = [int(year) for year in re.findall(r'(19\d{2}|20\d{2})', str(col))]
            
            if column_years:
                # Column has specific year(s) - create row only for those years
                for year in column_years:
                    long_row = {
                        'country': country,
                        'year': year,
                        'metric': clean_metric,
                        'value': value,
                        'source': 'Original Dataset',
                        'assumption': None
                    }
                    long_format_data.append(long_row)
            else:
                # Column has no specific year - create rows for all years found in dataset
                if unique_years:
                    for year in unique_years:
                        long_row = {
                            'country': country,
                            'year': year,
                            'metric': clean_metric,
                            'value': value,
                            'source': 'Original Dataset',
                            'assumption': None
                        }
                        long_format_data.append(long_row)
                else:
                    # No years found anywhere, create row with None
                    long_row = {
                        'country': country,
                        'year': None,
                        'metric': clean_metric,
                        'value': value,
                        'source': 'Original Dataset',
                        'assumption': None
                    }
                    long_format_data.append(long_row)
    
    # Create the final dataframe
    result_df = pd.DataFrame(long_format_data)
    
    return result_df

def pivot_with_assumptions(df, year):
    """
    Load CSV, filter by year, pivot metric values, and add a combined assumptions column per country.

    Returns:
    - pivot_df: DataFrame indexed by country, with metric columns and one 'assumptions' column.
    """
    
    # Handle None/NaN values in year column before converting to int
    df = df.copy()  # Don't modify original dataframe
    
    # Replace None/NaN with a default value or drop rows
    df['year'] = pd.to_numeric(df['year'], errors='coerce')  # Convert to NaN if can't convert
    
    # Option 1: Drop rows with invalid years
    df = df.dropna(subset=['year'])
    
    # Option 2: Or fill with a default year (uncomment if you prefer this)
    # df['year'] = df['year'].fillna(2023)  # Replace with appropriate default
    
    df['year'] = df['year'].astype(int)

    # Rest of your function remains the same...
    df_year = df[df['year'] == year]

    df_values = df_year.groupby(['country', 'metric'], as_index=False)['value'].mean()
    pivot_df = df_values.pivot(index='country', columns='metric', values='value')

    sources_per_country = (
        df_year.groupby('country')['source']
        .apply(lambda x: ', '.join(sorted(set(x.dropna().astype(str)))) if not x.dropna().empty else 'No source')
    )
    
    assumptions_per_country = (
        df_year.groupby('country')['assumption']
        .apply(lambda x: ', '.join(sorted(set(x.dropna().astype(str)))) if not x.dropna().empty else 'No assumption')
    )

    pivot_df['source'] = sources_per_country
    pivot_df['assumption'] = assumptions_per_country

    return pivot_df

def sparsity_ratio_column(df, col, sparse_value=None):
    """
    Calculate sparsity ratio of a column
    
    Parameters:
    df: DataFrame
    col: Column name
    sparse_value: Value to consider as sparse (None for NaN, 0 for zero, etc.)
    
    Returns:
    float: Sparsity ratio (0-1, where 1 means completely sparse)
    """
    if col not in df.columns:
        raise ValueError(f"Column '{col}' not found in DataFrame")
    
    total_count = len(df)
    
    if total_count == 0:
        return 0.0
    
    if sparse_value is None:
        # Count NaN/null values
        sparse_count = df[col].isnull().sum()
    else:
        # Count specific sparse value (including NaN)
        sparse_count = df[col].isnull().sum() + (df[col] == sparse_value).sum()
    
    sparsity_ratio = sparse_count / total_count
    return sparsity_ratio

def sparsity_ratio_row(df, row_index, sparse_value=None):
    """
    Calculate sparsity ratio of a row
    
    Parameters:
    df: DataFrame
    row_index: Row index
    sparse_value: Value to consider as sparse (None for NaN, 0 for zero, etc.)
    
    Returns:
    float: Sparsity ratio (0-1, where 1 means completely sparse)
    """
    if row_index not in df.index:
        raise ValueError(f"Row index '{row_index}' not found in DataFrame")
    
    row_data = df.loc[row_index]
    total_count = len(row_data)
    
    if total_count == 0:
        return 0.0
    
    if sparse_value is None:
        # Count NaN/null values
        sparse_count = row_data.isnull().sum()
    else:
        # Count specific sparse value (including NaN)
        sparse_count = row_data.isnull().sum() + (row_data == sparse_value).sum()
    
    sparsity_ratio = sparse_count / total_count
    return sparsity_ratio

def drop_sparse_columns(df, threshold=0.5, sparse_value=None):
    """
    Drop columns with insufficient data (high sparsity)
    
    Parameters:
    df: DataFrame
    threshold: Sparsity threshold (0-1, columns above this will be dropped)
    sparse_value: Value to consider as sparse (None for NaN, 0 for zero, etc.)
    
    Returns:
    DataFrame: DataFrame with sparse columns removed
    """
    if not 0 <= threshold <= 1:
        raise ValueError("Threshold must be between 0 and 1")
    
    df_copy = df.copy()
    columns_to_drop = []
    
    for col in df_copy.columns:
        sparsity = sparsity_ratio_column(df_copy, col, sparse_value)
        if sparsity > threshold:
            columns_to_drop.append(col)
    
    df_result = df_copy.drop(columns=columns_to_drop)
    
    return df_result

def drop_sparse_rows(df, threshold=0.5, sparse_value=None):
    """
    Drop rows with insufficient data (high sparsity)
    
    Parameters:
    df: DataFrame
    threshold: Sparsity threshold (0-1, rows above this will be dropped)
    sparse_value: Value to consider as sparse (None for NaN, 0 for zero, etc.)
    
    Returns:
    DataFrame: DataFrame with sparse rows removed
    """
    if not 0 <= threshold <= 1:
        raise ValueError("Threshold must be between 0 and 1")
    
    df_copy = df.copy()
    rows_to_drop = []
    
    for idx in df_copy.index:
        sparsity = sparsity_ratio_row(df_copy, idx, sparse_value)
        if sparsity > threshold:
            rows_to_drop.append(idx)
    
    df_result = df_copy.drop(index=rows_to_drop)
    
    return df_result

# Convenience functions for comprehensive sparsity analysis

def get_column_sparsity_summary(df, sparse_value=None):
    """
    Get sparsity summary for all columns
    
    Returns:
    DataFrame: Summary with columns, sparsity ratios, and recommendations
    """
    summary_data = []
    
    for col in df.columns:
        sparsity = sparsity_ratio_column(df, col, sparse_value)
        total_values = len(df)
        sparse_count = int(sparsity * total_values)
        non_sparse_count = total_values - sparse_count
        
        # Recommendation based on sparsity
        if sparsity < 0.1:
            recommendation = "Excellent - Keep column"
        elif sparsity < 0.3:
            recommendation = "Good - Keep column"
        elif sparsity < 0.5:
            recommendation = "Fair - Consider imputation"
        elif sparsity < 0.7:
            recommendation = "Poor - Consider dropping"
        else:
            recommendation = "Very Poor - Drop column"
        
        summary_data.append({
            'column': col,
            'sparsity_ratio': sparsity,
            'sparse_count': sparse_count,
            'non_sparse_count': non_sparse_count,
            'total_count': total_values,
            'recommendation': recommendation
        })
    
    summary_df = pd.DataFrame(summary_data)
    return summary_df.sort_values('sparsity_ratio', ascending=False)

def get_row_sparsity_summary(df, sparse_value=None, top_n=10):
    """
    Get sparsity summary for rows
    
    Returns:
    DataFrame: Summary with row indices, sparsity ratios, and counts
    """
    summary_data = []
    
    for idx in df.index:
        sparsity = sparsity_ratio_row(df, idx, sparse_value)
        total_values = len(df.columns)
        sparse_count = int(sparsity * total_values)
        non_sparse_count = total_values - sparse_count
        
        if sparsity < 0.1:
            recommendation = "Excellent - Keep column"
        elif sparsity < 0.3:
            recommendation = "Good - Keep column"
        elif sparsity < 0.5:
            recommendation = "Fair - Consider imputation"
        elif sparsity < 0.7:
            recommendation = "Poor - Consider dropping"
        else:
            recommendation = "Very Poor - Drop column"

        summary_data.append({
            'row_index': idx,
            'sparsity_ratio': sparsity,
            'sparse_count': sparse_count,
            'non_sparse_count': non_sparse_count,
            'total_count': total_values,
            'recommendation': recommendation
        })
    
    summary_df = pd.DataFrame(summary_data)
    summary_df = summary_df.sort_values('sparsity_ratio', ascending=False)
    
    if top_n:
        return summary_df.head(top_n)
    
    return summary_df

def analyze_sparsity_patterns(df, sparse_value=None):
    """
    Comprehensive sparsity analysis
    
    Returns:
    dict: Comprehensive sparsity analysis results
    """
    total_elements = df.shape[0] * df.shape[1]
    
    if sparse_value is None:
        total_sparse = df.isnull().sum().sum()
    else:
        total_sparse = df.isnull().sum().sum() + (df == sparse_value).sum().sum()
    
    overall_sparsity = total_sparse / total_elements if total_elements > 0 else 0
    
    # Column analysis
    col_sparsity = [sparsity_ratio_column(df, col, sparse_value) for col in df.columns]
    
    # Row analysis
    row_sparsity = [sparsity_ratio_row(df, idx, sparse_value) for idx in df.index]
    
    results = {
        'overall_sparsity': overall_sparsity,
        'total_elements': total_elements,
        'total_sparse': total_sparse,
        'column_stats': {
            'mean_sparsity': np.mean(col_sparsity),
            'median_sparsity': np.median(col_sparsity),
            'min_sparsity': np.min(col_sparsity),
            'max_sparsity': np.max(col_sparsity),
            'std_sparsity': np.std(col_sparsity)
        },
        'row_stats': {
            'mean_sparsity': np.mean(row_sparsity),
            'median_sparsity': np.median(row_sparsity),
            'min_sparsity': np.min(row_sparsity),
            'max_sparsity': np.max(row_sparsity),
            'std_sparsity': np.std(row_sparsity)
        },
        'recommendations': {
            'columns_to_drop_50pct': [col for col in df.columns if sparsity_ratio_column(df, col, sparse_value) > 0.5],
            'columns_to_drop_70pct': [col for col in df.columns if sparsity_ratio_column(df, col, sparse_value) > 0.7],
            'rows_to_drop_50pct': len([idx for idx in df.index if sparsity_ratio_row(df, idx, sparse_value) > 0.5]),
            'rows_to_drop_70pct': len([idx for idx in df.index if sparsity_ratio_row(df, idx, sparse_value) > 0.7])
        }
    }
    
    return results

def optimize_dataframe_sparsity(df, column_threshold=0.5, row_threshold=0.5, sparse_value=None):
    """
    Optimize dataframe by removing sparse columns and rows
    
    Returns:
    dict: Optimized dataframe and optimization report
    """
    original_shape = df.shape
    
    # Step 1: Remove sparse columns
    df_step1 = drop_sparse_columns(df, column_threshold, sparse_value)
    
    # Step 2: Remove sparse rows
    df_optimized = drop_sparse_rows(df_step1, row_threshold, sparse_value)
    
    final_shape = df_optimized.shape
    
    report = {
        'original_shape': original_shape,
        'final_shape': final_shape,
        'columns_removed': original_shape[1] - final_shape[1],
        'rows_removed': original_shape[0] - final_shape[0],
        'data_retention': (final_shape[0] * final_shape[1]) / (original_shape[0] * original_shape[1]) if original_shape[0] * original_shape[1] > 0 else 0,
        'column_threshold': column_threshold,
        'row_threshold': row_threshold,
        'sparse_value': sparse_value
    }
    
    return {
        'optimized_df': df_optimized,
        'report': report
    }

def compare_sparsity_thresholds(df, thresholds=[0.3, 0.5, 0.7, 0.9], sparse_value=None):
    """
    Compare different sparsity thresholds and their impact
    
    Returns:
    DataFrame: Comparison results for different thresholds
    """
    comparison_data = []
    original_shape = df.shape
    
    for threshold in thresholds:
        # Test column dropping
        df_col_dropped = drop_sparse_columns(df, threshold, sparse_value)
        
        # Test row dropping
        df_row_dropped = drop_sparse_rows(df, threshold, sparse_value)
        
        # Test both
        df_both = drop_sparse_rows(
            drop_sparse_columns(df, threshold, sparse_value),
            threshold, sparse_value
        )
        
        comparison_data.append({
            'threshold': threshold,
            'columns_remaining': df_col_dropped.shape[1],
            'rows_remaining_col_drop': df_col_dropped.shape[0],
            'rows_remaining_row_drop': df_row_dropped.shape[0],
            'columns_remaining_row_drop': df_row_dropped.shape[1],
            'final_shape_both': df_both.shape,
            'data_retention_both': (df_both.shape[0] * df_both.shape[1]) / (original_shape[0] * original_shape[1]) if original_shape[0] * original_shape[1] > 0 else 0
        })
    
    return pd.DataFrame(comparison_data)

def identify_sparse_value_candidates(df, sample_size=1000):
    """
    Identify potential sparse values in the dataset
    
    Returns:
    dict: Potential sparse values and their frequencies
    """
    candidates = {}
    
    # Sample the dataframe if it's large
    if len(df) > sample_size:
        sampled_df = df.sample(n=sample_size, random_state=42)
    else:
        sampled_df = df
    
    for col in sampled_df.select_dtypes(include=[np.number]).columns:
        value_counts = sampled_df[col].value_counts()
        total_non_null = sampled_df[col].count()
        
        if total_non_null > 0:
            # Look for values that appear frequently and might be sparse indicators
            for value, count in value_counts.head(5).items():
                frequency = count / total_non_null
                if frequency > 0.1:  # If value appears in more than 10% of non-null values
                    if value not in candidates:
                        candidates[value] = []
                    candidates[value].append({
                        'column': col,
                        'frequency': frequency,
                        'count': count
                    })
    
    return candidates

def cluster_no(df, features, k_min=1, k_max=10, random_state=42, display_data = False):
    import numpy as np
    from sklearn.cluster import KMeans
    import matplotlib.pyplot as plt
    
    X = df[features].copy()
    k_rng = range(k_min, k_max + 1)
    sse = []
    
    for k in k_rng:
        km = KMeans(n_clusters=k, random_state=random_state)
        km.fit(X)
        sse.append(km.inertia_)
    
    # Method 1: Maximum distance to line (your original approach, corrected)
    def distance_to_line(point, line_start, line_end):
        """Calculate perpendicular distance from point to line segment"""
        # Vector from line_start to line_end
        line_vec = line_end - line_start
        # Vector from line_start to point
        point_vec = point - line_start
        
        # Project point onto line
        line_len_sq = np.dot(line_vec, line_vec)
        if line_len_sq == 0:
            return np.linalg.norm(point_vec)
        
        # Calculate projection parameter
        t = np.dot(point_vec, line_vec) / line_len_sq
        
        # Find closest point on line segment
        if t < 0:
            closest_point = line_start
        elif t > 1:
            closest_point = line_end
        else:
            closest_point = line_start + t * line_vec
        
        # Return distance to closest point
        return np.linalg.norm(point - closest_point)
    
    # Create points for distance calculation
    k_values = np.array(list(k_rng))
    sse_values = np.array(sse)
    
    # Normalize the data for better distance calculation
    k_norm = (k_values - k_values.min()) / (k_values.max() - k_values.min())
    sse_norm = (sse_values - sse_values.min()) / (sse_values.max() - sse_values.min())
    
    points = np.column_stack((k_norm, sse_norm))
    line_start = points[0]
    line_end = points[-1]
    
    # Calculate distances
    distances = np.array([distance_to_line(p, line_start, line_end) for p in points])
    
    # Find elbow point (maximum distance)
    elbow_idx = distances.argmax()
    optimal_k_method1 = k_values[elbow_idx]
    
    # Method 2: Second derivative approach (alternative method)
    def second_derivative_method(sse_values):
        """Find elbow using second derivative"""
        if len(sse_values) < 3:
            return 1
        
        # Calculate first derivative (rate of change)
        first_deriv = np.diff(sse_values)
        
        # Calculate second derivative (rate of change of rate of change)
        second_deriv = np.diff(first_deriv)
        
        # Find point where second derivative is maximum (most curvature)
        # Add 2 because we lost 2 points in double differentiation
        elbow_idx = np.argmax(second_deriv) + 2
        return k_values[elbow_idx]
    
    optimal_k_method2 = second_derivative_method(sse_values)
    
    # Method 3: Percentage change approach
    def percentage_change_method(sse_values, threshold=0.1):
        """Find elbow where percentage improvement drops below threshold"""
        pct_improvements = []
        for i in range(1, len(sse_values)):
            pct_improvement = (sse_values[i-1] - sse_values[i]) / sse_values[i-1]
            pct_improvements.append(pct_improvement)
        
        # Find first point where improvement drops below threshold
        for i, improvement in enumerate(pct_improvements):
            if improvement < threshold:
                return k_values[i + 1] # +1 because we started from index 1
        
        # If no point found, return the middle value
        return k_values[len(k_values)//2]
    
    optimal_k_method3 = percentage_change_method(sse_values)
    if display_data:
        # Plotting for visualization
        plt.figure(figsize=(12, 4))
        
        # Plot 1: SSE vs K with elbow points
        plt.subplot(1, 3, 1)
        plt.plot(k_values, sse_values, 'bo-', markersize=8)
        plt.axvline(x=optimal_k_method1, color='r', linestyle='--', label=f'Max Distance: {optimal_k_method1}')
        plt.axvline(x=optimal_k_method2, color='g', linestyle='--', label=f'2nd Derivative: {optimal_k_method2}')
        plt.axvline(x=optimal_k_method3, color='purple', linestyle='--', label=f'Pct Change: {optimal_k_method3}')
        plt.xlabel('Number of Clusters (k)')
        plt.ylabel('SSE (Inertia)')
        plt.title('Elbow Method - SSE vs K')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Plot 2: Distance to line
        plt.subplot(1, 3, 2)
        plt.plot(k_values, distances, 'ro-', markersize=8)
        plt.axvline(x=optimal_k_method1, color='r', linestyle='--')
        plt.xlabel('Number of Clusters (k)')
        plt.ylabel('Distance to Line')
        plt.title('Distance to Line Method')
        plt.grid(True, alpha=0.3)
        
        # Plot 3: Second derivative
        plt.subplot(1, 3, 3)
        if len(sse_values) >= 3:
            second_deriv = np.diff(np.diff(sse_values))
            plt.plot(k_values[2:], second_deriv, 'go-', markersize=8)
            plt.axvline(x=optimal_k_method2, color='g', linestyle='--')
        plt.xlabel('Number of Clusters (k)')
        plt.ylabel('Second Derivative')
        plt.title('Second Derivative Method')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        print(f"Optimal k recommendations:")
        print(f"Method 1 (Max Distance to Line): {optimal_k_method1}")
        print(f"Method 2 (Second Derivative): {optimal_k_method2}")
        print(f"Method 3 (Percentage Change): {optimal_k_method3}")
        
    # Return the most commonly suggested value, or method 1 if all different
    methods = [optimal_k_method1, optimal_k_method2, optimal_k_method3]
    # Find most common value
    from collections import Counter
    counter = Counter(methods)
    most_common = counter.most_common(1)[0][0]

    import numpy as np
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
    import matplotlib.pyplot as plt
    k_candidates = methods
    X = df[features].copy()
    
    results = {}
    
    for k in k_candidates:
        km = KMeans(n_clusters=k, random_state=random_state)
        labels = km.fit_predict(X)
        
        # Calculate validation metrics
        silhouette = silhouette_score(X, labels)
        calinski_harabasz = calinski_harabasz_score(X, labels)
        davies_bouldin = davies_bouldin_score(X, labels)
        
        results[k] = {
            'silhouette': silhouette,
            'calinski_harabasz': calinski_harabasz,
            'davies_bouldin': davies_bouldin,
            'inertia': km.inertia_
        }
    
    # Create comparison table
    if display_data:
        print("Cluster Validation Results:")
        print("=" * 80)
        print(f"{'k':<3} {'Silhouette':<12} {'Calinski-H':<12} {'Davies-B':<12} {'Inertia':<12}")
        print("-" * 80)
    
        for k in k_candidates:
            r = results[k]
            print(f"{k:<3} {r['silhouette']:<12.4f} {r['calinski_harabasz']:<12.2f} {r['davies_bouldin']:<12.4f} {r['inertia']:<12.2f}")
    
        print("\nInterpretation:")
        print("- Silhouette Score: Higher is better (range: -1 to 1)")
        print("- Calinski-Harabasz: Higher is better")
        print("- Davies-Bouldin: Lower is better")
        print("- Inertia: Lower is better (but consider elbow)")
    
        # Find best k for each metric
        best_silhouette = max(results.keys(), key=lambda k: results[k]['silhouette'])
        best_calinski = max(results.keys(), key=lambda k: results[k]['calinski_harabasz'])
        best_davies = min(results.keys(), key=lambda k: results[k]['davies_bouldin'])
        
        print(f"\nBest k by metric:")
        print(f"- Silhouette Score: k={best_silhouette}")
        print(f"- Calinski-Harabasz: k={best_calinski}")
        print(f"- Davies-Bouldin: k={best_davies}")
    
    # Scoring system to find overall best
    scores = {k: 0 for k in k_candidates}
    # Rank each metric (3 points for best, 2 for second, 1 for third)
    metrics_rankings = {
        'silhouette': sorted(k_candidates, key=lambda k: results[k]['silhouette'], reverse=True),
        'calinski_harabasz': sorted(k_candidates, key=lambda k: results[k]['calinski_harabasz'], reverse=True),
        'davies_bouldin': sorted(k_candidates, key=lambda k: results[k]['davies_bouldin'])
    }
    points = [3, 2, 1]
    for metric, ranking in metrics_rankings.items():
        for i, k in enumerate(ranking):
            scores[k] += points[i]
    
    best_overall = max(scores.keys(), key=lambda k: scores[k])
    if display_data:
        print(f"\nOverall ranking (based on combined metrics):")
        for k in sorted(scores.keys(), key=lambda k: scores[k], reverse=True):
            print(f"k={k}: {scores[k]} points")
        
        print(f"\n🎯 RECOMMENDATION: k={best_overall}")
    
    return best_overall

def get_kmeans_labels(df, features, n_clusters = 3, random_state = 42):
    from sklearn.cluster import KMeans
    X = df[features]
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state)
    kmeans.fit(X)
    return kmeans.labels_

def advanced_cluster_analysis(df, selected_features, feature_weights, exclude_countries=None, 
                            n_clusters=3, max_clusters=6, show_elbow=True, generate_rules=True,
                            show_pca_loadings=True, loading_threshold=0.5, random_state=42):
    """
    Advanced clustering analysis with PCA, decision trees, and comprehensive visualization
    """
    import pandas as pd
    import numpy as np
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    from sklearn.tree import DecisionTreeClassifier, _tree
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    results = {}
    
    # Prepare data
    data = df.copy()
    if 'country' in data.columns:
        country_col = 'country'
    else:
        country_col = None
    
    # Exclude countries if specified
    if exclude_countries and country_col:
        data = data[~data[country_col].isin(exclude_countries)]
    
    # Filter data based on selected features (remove rows with missing or zero values)
    if country_col:
        data_selected = data[[country_col] + selected_features].copy()
    else:
        data_selected = data[selected_features].copy()
    
    # Remove rows with missing or zero values in selected features
    mask_na = data_selected[selected_features].isna().any(axis=1)
    mask_zero = (data_selected[selected_features] == 0).any(axis=1)
    dropped_mask = mask_na | mask_zero
    
    data_cleaned = data_selected.loc[~dropped_mask].reset_index(drop=True)
    
    if len(data_cleaned) < n_clusters:
        raise ValueError(f"Not enough valid data points ({len(data_cleaned)}) for {n_clusters} clusters")
    
    # PCA Analysis
    if show_pca_loadings:
        scaler_pca = StandardScaler()
        pca_data_scaled = scaler_pca.fit_transform(data_cleaned[selected_features])
        
        pca = PCA()
        pca.fit(pca_data_scaled)
        
        loadings = pca.components_.T * np.sqrt(pca.explained_variance_)
        loadings_df = pd.DataFrame(
            loadings, 
            index=selected_features,
            columns=[f'PC{i+1}' for i in range(loadings.shape[1])]
        )
        results['pca_loadings'] = loadings_df.round(4)
        
        # Identify important features
        important_features = set()
        for i in range(loadings.shape[1]):
            comp_loadings = loadings_df.iloc[:, i]
            sig_feats = comp_loadings[comp_loadings.abs() > loading_threshold].index
            important_features.update(sig_feats)
        results['important_features'] = list(important_features)
    
    # Standardize and weight features
    scaler_clustering = StandardScaler()
    standardized_data = scaler_clustering.fit_transform(data_cleaned[selected_features])
    standardized_df = pd.DataFrame(standardized_data, columns=selected_features)
    
    # Apply weights
    for feature in selected_features:
        weight = feature_weights.get(feature, 1)
        standardized_df[feature] = standardized_df[feature] * weight
    
    weighted_data = standardized_df.values
    
    # Elbow Method
    if show_elbow:
        K_max = min(max_clusters + 1, len(data_cleaned))
        inertia = []
        K_range = range(1, K_max + 1)
        
        for K in K_range:
            if K <= len(data_cleaned):
                kmeans = KMeans(n_clusters=K, random_state=random_state, n_init=10)
                kmeans.fit(weighted_data)
                inertia.append(kmeans.inertia_)
        
        fig_elbow, ax = plt.subplots(figsize=(10, 6))
        ax.plot(K_range[:len(inertia)], inertia, marker='o', linewidth=2, markersize=8)
        ax.set_title('Elbow Method for Optimal K', fontsize=14)
        ax.set_xlabel('Number of Clusters (K)', fontsize=12)
        ax.set_ylabel('Inertia', fontsize=12)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        results['elbow_fig'] = fig_elbow
    
    # Perform clustering
    kmeans_final = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    cluster_labels = kmeans_final.fit_predict(weighted_data)
    
    # Calculate silhouette score
    if len(set(cluster_labels)) > 1:
        silhouette_avg = silhouette_score(weighted_data, cluster_labels)
    else:
        silhouette_avg = 0
    results['silhouette_score'] = silhouette_avg
    
    # Create results dataframe
    clustered_data = data_cleaned.copy()
    clustered_data['Cluster'] = cluster_labels + 1  # Start clusters from 1
    
    # Sort clusters by highest weighted feature
    highest_weight_feature = max(feature_weights, key=feature_weights.get)
    cluster_means = clustered_data.groupby('Cluster')[highest_weight_feature].mean()
    sorted_clusters = cluster_means.sort_values(ascending=False).index.tolist()
    
    # Remap cluster labels based on sorting
    cluster_mapping = {old: new for new, old in enumerate(sorted_clusters, 1)}
    clustered_data['Cluster'] = clustered_data['Cluster'].map(cluster_mapping)
    
    # Sort final dataframe
    clustered_data = clustered_data.sort_values(['Cluster', highest_weight_feature], 
                                              ascending=[True, False])
    
    results['clustered_data'] = clustered_data
    
    # Decision Tree Rules
    if generate_rules:
        try:
            dt_clf = DecisionTreeClassifier(random_state=random_state, max_depth=5)
            dt_clf.fit(standardized_df, clustered_data['Cluster'])
            
            rules_df = extract_decision_rules(dt_clf, selected_features, feature_weights, scaler_clustering)
            results['decision_rules'] = rules_df
        except Exception as e:
            print(f"Could not generate decision tree rules: {e}")
    
    # Visualization
    fig_cluster = create_cluster_visualization(
        clustered_data, selected_features, weighted_data, country_col, n_clusters
    )
    results['cluster_plot'] = fig_cluster
    
    return results

def extract_decision_rules(tree, feature_names, feature_weights, scaler):
    """Extract decision tree rules with original scale thresholds"""
    tree_ = tree.tree_
    feature = tree_.feature
    threshold = tree_.threshold
    children_left = tree_.children_left
    children_right = tree_.children_right
    value = tree_.value

    means = scaler.mean_
    stds = np.sqrt(scaler.var_)

    def convert_threshold(feat_idx, thresh):
        feat_name = feature_names[feat_idx]
        w = feature_weights.get(feat_name, 1)
        mean = means[feat_idx]
        std = stds[feat_idx]
        return (thresh / w) * std + mean

    paths = []
    path_conditions = []

    def recurse(node):
        if children_left[node] == tree.TREE_LEAF and children_right[node] == tree.TREE_LEAF:
            class_id = np.argmax(value[node][0])
            rule = " & ".join(path_conditions) if path_conditions else "All data"
            paths.append({'Rule': rule, 'Predicted_Cluster': int(class_id) + 1})
        else:
            feat_idx = feature[node]
            feat_name = feature_names[feat_idx]
            thresh = threshold[node]
            thresh_orig = convert_threshold(feat_idx, thresh)

            # Left child: feature <= threshold
            path_conditions.append(f"{feat_name} <= {thresh_orig:.3f}")
            recurse(children_left[node])
            path_conditions.pop()

            # Right child: feature > threshold
            path_conditions.append(f"{feat_name} > {thresh_orig:.3f}")
            recurse(children_right[node])
            path_conditions.pop()

    recurse(0)
    return pd.DataFrame(paths)

def create_cluster_visualization(clustered_data, selected_features, weighted_data, country_col, n_clusters):
    """Create cluster visualization"""
    
    if len(selected_features) >= 3:
        # For 3+ features, show both direct plot (first 2 features) and PCA plot
        fig, axes = plt.subplots(1, 2, figsize=(20, 8))
        
        # Left plot: First two features direct visualization
        ax1 = axes[0]
        scatter1 = ax1.scatter(
            clustered_data[selected_features[0]], 
            clustered_data[selected_features[1]], 
            c=clustered_data['Cluster'], 
            cmap='viridis', 
            alpha=0.7, 
            s=100, 
            edgecolor='black',
            linewidth=0.5
        )
        
        if country_col and country_col in clustered_data.columns:
            for i in range(len(clustered_data)):
                ax1.annotate(
                    clustered_data[country_col].iloc[i], 
                    (clustered_data[selected_features[0]].iloc[i], 
                     clustered_data[selected_features[1]].iloc[i]), 
                    fontsize=8, alpha=0.8, ha='center'
                )
        
        ax1.set_title(f'{selected_features[0]} vs {selected_features[1]}', fontsize=12)
        ax1.set_xlabel(selected_features[0], fontsize=10)
        ax1.set_ylabel(selected_features[1], fontsize=10)
        ax1.grid(True, alpha=0.3)
        plt.colorbar(scatter1, ax=ax1, label='Cluster')
        
        # Right plot: PCA visualization (THIS WAS MISSING!)
        from sklearn.decomposition import PCA
        
        pca_vis = PCA(n_components=2)
        reduced_data = pca_vis.fit_transform(weighted_data)
        
        ax2 = axes[1]
        scatter2 = ax2.scatter(
            reduced_data[:, 0], 
            reduced_data[:, 1], 
            c=clustered_data['Cluster'], 
            cmap='viridis', 
            alpha=0.7, 
            s=100, 
            edgecolor='black',
            linewidth=0.5
        )
        
        if country_col and country_col in clustered_data.columns:
            for i in range(len(clustered_data)):
                ax2.annotate(
                    clustered_data[country_col].iloc[i], 
                    (reduced_data[i, 0], reduced_data[i, 1]), 
                    fontsize=8, alpha=0.8, ha='center'
                )
        
        ax2.set_title('PCA Cluster Visualization (All Features)', fontsize=12)
        ax2.set_xlabel(f'PC1 ({pca_vis.explained_variance_ratio_[0]:.2%} variance)', fontsize=10)
        ax2.set_ylabel(f'PC2 ({pca_vis.explained_variance_ratio_[1]:.2%} variance)', fontsize=10)
        ax2.grid(True, alpha=0.3)
        plt.colorbar(scatter2, ax=ax2, label='Cluster')
        
    else:
        # For exactly 2 features, show only direct plot
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        
        scatter = ax.scatter(
            clustered_data[selected_features[0]], 
            clustered_data[selected_features[1]], 
            c=clustered_data['Cluster'], 
            cmap='viridis', 
            alpha=0.7, 
            s=100, 
            edgecolor='black',
            linewidth=0.5
        )
        
        if country_col and country_col in clustered_data.columns:
            for i in range(len(clustered_data)):
                ax.annotate(
                    clustered_data[country_col].iloc[i], 
                    (clustered_data[selected_features[0]].iloc[i], 
                     clustered_data[selected_features[1]].iloc[i]), 
                    fontsize=8, alpha=0.8, ha='center'
                )
        
        ax.set_title(f'Cluster Visualization: {selected_features[0]} vs {selected_features[1]}', fontsize=14)
        ax.set_xlabel(selected_features[0], fontsize=12)
        ax.set_ylabel(selected_features[1], fontsize=12)
        ax.grid(True, alpha=0.3)
        plt.colorbar(scatter, ax=ax, label='Cluster')
    
    plt.tight_layout()
    return fig


def identify_insufficient_data_countries(df, min_data_threshold=0.8):
    """
    Identify countries with insufficient data based on a minimum data coverage threshold
    
    Parameters:
    df: DataFrame with countries as index or 'Country' column
    min_data_threshold: Minimum proportion of non-null values required (default 0.8)
    
    Returns:
    List of countries with insufficient data coverage
    """
    # Make a copy to avoid modifying original
    data = df.copy()
    
    # Handle country column/index
    if 'country' in data.columns:
        data = data.set_index('country')
    
    # Calculate data coverage for each country (row)
    total_columns = len(data.columns)
    data_coverage = data.notna().sum(axis=1) / total_columns
    
    # Identify countries below threshold
    insufficient_countries = data_coverage[data_coverage < min_data_threshold].index.tolist()
    
    return insufficient_countries

def classify_countries(df, min_data_threshold=0.8, insufficient_label='Insufficient Data'):
    """
    Classify countries, labeling those with insufficient data using a specified label
    
    Parameters:
    df: DataFrame with countries as index or 'Country' column
    min_data_threshold: Minimum proportion of non-null values required (default 0.8)
    insufficient_label: Label to assign to countries with insufficient data
    
    Returns:
    DataFrame with added 'Classification' column
    """
    # Make a copy to avoid modifying original
    result_df = df.copy()
    
    # Ensure Country is a column for easier handling
    country_col_added = False
    if 'country' not in result_df.columns:
        result_df = result_df.reset_index()
        if 'index' in result_df.columns:
            result_df = result_df.rename(columns={'index': 'country'})
        country_col_added = True
    
    # Get countries with insufficient data
    insufficient_countries = identify_insufficient_data_countries(df, min_data_threshold)
    
    # Create classification column
    result_df['Classification'] = 'Sufficient Data'
    
    # Mark countries with insufficient data
    insufficient_mask = result_df['country'].isin(insufficient_countries)
    result_df.loc[insufficient_mask, 'Classification'] = insufficient_label
    
    # Calculate and add data coverage information
    data_cols = [col for col in result_df.columns if col not in ['country', 'Classification']]
    if data_cols:
        result_df['Data_Coverage'] = result_df[data_cols].notna().sum(axis=1) / len(data_cols)
    else:
        result_df['Data_Coverage'] = 0.0
    
    # Add summary statistics
    total_countries = len(result_df)
    insufficient_count = len(insufficient_countries)
    sufficient_count = total_countries - insufficient_count
    
    # Store summary as attributes (for optional access)
    result_df.attrs['summary'] = {
        'total_countries': total_countries,
        'sufficient_data_countries': sufficient_count,
        'insufficient_data_countries': insufficient_count,
        'insufficient_percentage': (insufficient_count / total_countries) * 100,
        'threshold_used': min_data_threshold,
        'insufficient_label': insufficient_label
    }
    
    return result_df

def get_classification_summary(df):
    """
    Get detailed summary of country classifications
    
    Parameters:
    df: DataFrame with Classification column
    
    Returns:
    Dictionary with classification summary statistics
    """
    if 'Classification' not in df.columns:
        raise ValueError("DataFrame must contain 'Classification' column")
    
    # Basic classification counts
    classification_counts = df['Classification'].value_counts()
    total_countries = len(df)
    
    summary = {
        'total_countries': total_countries,
        'classification_counts': classification_counts.to_dict(),
        'classification_percentages': (classification_counts / total_countries * 100).to_dict()
    }
    
    # Add data coverage statistics if available
    if 'Data_Coverage' in df.columns:
        summary['data_coverage_stats'] = {
            'mean_coverage': df['Data_Coverage'].mean(),
            'median_coverage': df['Data_Coverage'].median(),
            'min_coverage': df['Data_Coverage'].min(),
            'max_coverage': df['Data_Coverage'].max(),
            'std_coverage': df['Data_Coverage'].std()
        }
    
    # Add fallback information if available
    if 'Fallback_Applied' in df.columns:
        fallback_count = df['Fallback_Applied'].sum()
        summary['fallback_stats'] = {
            'total_fallbacks_applied': fallback_count,
            'fallback_percentage': (fallback_count / total_countries) * 100
        }
    
    return summary


def analyze_data_coverage_patterns(df, min_data_threshold=0.8):
    """
    Analyze data coverage patterns across countries
    
    Parameters:
    df: DataFrame with countries as index or 'Country' column
    min_data_threshold: Threshold for sufficient data
    
    Returns:
    Dictionary with detailed coverage analysis
    """
    # Make a copy and handle country column/index
    data = df.copy()
    if 'country' in data.columns:
        countries = data['country'].values
        data = data.set_index('country')
    else:
        countries = data.index.values
    
    # Calculate coverage for each country
    total_columns = len(data.columns)
    coverage_by_country = data.notna().sum(axis=1) / total_columns
    
    # Calculate coverage for each feature
    coverage_by_feature = data.notna().sum(axis=0) / len(data)
    
    # Identify patterns
    sufficient_countries = coverage_by_country[coverage_by_country >= min_data_threshold]
    insufficient_countries = coverage_by_country[coverage_by_country < min_data_threshold]
    
    # Feature completeness analysis
    complete_features = coverage_by_feature[coverage_by_feature == 1.0]
    incomplete_features = coverage_by_feature[coverage_by_feature < 1.0]
    sparse_features = coverage_by_feature[coverage_by_feature < 0.5]
    
    analysis = {
        'coverage_summary': {
            'mean_country_coverage': coverage_by_country.mean(),
            'median_country_coverage': coverage_by_country.median(),
            'min_country_coverage': coverage_by_country.min(),
            'max_country_coverage': coverage_by_country.max(),
            'std_country_coverage': coverage_by_country.std()
        },
        'country_classification': {
            'sufficient_data_countries': len(sufficient_countries),
            'insufficient_data_countries': len(insufficient_countries),
            'threshold_used': min_data_threshold
        },
        'feature_analysis': {
            'total_features': len(coverage_by_feature),
            'complete_features': len(complete_features),
            'incomplete_features': len(incomplete_features),
            'sparse_features': len(sparse_features),
            'mean_feature_coverage': coverage_by_feature.mean()
        },
        'detailed_coverage': {
            'by_country': coverage_by_country.to_dict(),
            'by_feature': coverage_by_feature.to_dict()
        }
    }
    
    return analysis


if __name__ == "__main__":
    main()
