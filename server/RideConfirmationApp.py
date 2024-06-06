from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy import platform

class RideConfirmationApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        self.confirm_button = Button(text='Confirm Ride')
        self.confirm_button.bind(on_press=self.confirm_ride)
        layout.add_widget(self.confirm_button)
        self.message_label = Label(text='')
        layout.add_widget(self.message_label)
        return layout

    def confirm_ride(self, instance):
        # Simulate ride confirmation logic
        if platform == 'android':
            self.message_label.text = "Ride confirmed!"
        else:
            self.message_label.text = "Ride confirmation not supported on this platform."

if __name__ == '__main__':
    RideConfirmationApp().run()
