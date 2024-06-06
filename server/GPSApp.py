import kivy
from kivy.app import App
from kivy.uix.button import Button
from jnius import autoclass
import os
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy import platform
from plyer import filechooser
import sys


#pip install kivy
#pip install kivy-garden
#garden install android_permissions
#pip install cython
#pip install jnius
#pip install plyer
#garden install android_permissions

if platform == "android":
             from android.permissions import request_permissions, Permission, check_permission  # pylint: disable=import-error # type: ignore
             
             permissions = [Permission.READ_EXTERNAL_STORAGE,
                            Permission.WRITE_EXTERNAL_STORAGE,
                            Permission.ACCESS_COARSE_LOCATION,
                            Permission.ACCESS_FINE_LOCATION]
                
                # Request permissions
             request_permissions(permissions)
                
                # Check if permissions are granted
             for permission in permissions:
                if not check_permission(permission):
                    print(f"Permission {permission} not granted.")
                    # Handle permission denial here
                    # You might want to inform the user or take appropriate action

          



class GPSApp(App):

    def build(self):
        request_permissions([Permission.ACCESS_COARSE_LOCATION, Permission.ACCESS_FINE_LOCATION])       

        button = Button(text='Get Location', size_hint=(None, None), size=(200, 50))
        button.bind(on_release=self.get_location)
        return button

    def get_location(self, instance=None):
        Criteria = autoclass('android.location.Criteria')
        locationManager = autoclass('android.content.Context').getSystemService(App.PythonActivity.LOCATION_SERVICE)
        provider = locationManager.getBestProvider(Criteria(), False)
        location = locationManager.getLastKnownLocation(provider)
        if location:
            latitude = location.getLatitude()
            longitude = location.getLongitude()
            print("Latitude:", latitude)
            print("Longitude:", longitude)
        else:
            print("Location not available.")

if __name__ == '__main__':
    GPSApp().run()
