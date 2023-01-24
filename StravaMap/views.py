from django.shortcuts import render
import folium
import requests
import pandas as pd
import polyline

# Create your views here.
def base_map(request):
    # Make your map object
    main_map = folium.Map(location=[43.45, -80.476], zoom_start = 12) # Create base map
    main_map_html = main_map._repr_html_() # Get HTML for website

    context = {
        "main_map":main_map_html
    }
    return render(request, 'index.html', context)

def connected_map(request):
    # Make your map object
    main_map = folium.Map(location=[43.45, -80.476], zoom_start = 12) # Create base map
    user = request.user # Pulls in the Strava User data
    strava_login = user.social_auth.get(provider='strava') # Strava login
    access_token = strava_login.extra_data['access_token'] # Strava Access token
    activites_url = "https://www.strava.com/api/v3/athlete/activities"

    # Get activity data
    header = {'Authorization': 'Bearer ' + str(access_token)}
    activity_df_list = []
    for n in range(5):  # Change this to be higher if you have more than 1000 activities
        param = {'per_page': 200, 'page': n + 1}

        activities_json = requests.get(activites_url, headers=header, params=param).json()
        if not activities_json:
            break
        activity_df_list.append(pd.json_normalize(activities_json))

    # Get Polyline Data
    activities_df = pd.concat(activity_df_list)
    activities_df = activities_df.dropna(subset=['map.summary_polyline'])
    activities_df['polylines'] = activities_df['map.summary_polyline'].apply(polyline.decode)

    # Plot Polylines onto Folium Map
    for pl in activities_df['polylines']:
        if len(pl) > 0: # Ignore polylines with length zero (Thanks Joukesmink for the tip)
            folium.PolyLine(locations=pl, color='red').add_to(main_map)

    # Return HTML version of map
    main_map_html = main_map._repr_html_() # Get HTML for website
    context = {
        "main_map":main_map_html
    }
    return render(request, 'index.html', context)

# from django.shortcuts import render, redirect
# from django.http import HttpResponse
# import folium
#
# # Create your views here.
#
#
# def main_map(request):
#     # Create Map Object
#     main_map = folium.Map(location=[19, -12], zoom_start=2)
#
#     # folium.Marker([39.09616, -117.80612], tooltip='Click for more',
#     #               popup='United States').add_to(main_map)
#     # Get HTML Representation of Map Object
#     main_map = main_map._repr_html_()
#     context = {
#         'main_map': main_map,
#         'form': 'potato',
#     }
#     return render(request, 'index.html', context)