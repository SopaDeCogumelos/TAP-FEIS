import os
import sys

# Adiciona o diretório atual ao path para garantir importação correta
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from tuya_lib import DeviceManager

class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 10

        # Inicializa o gerenciador
        self.manager = DeviceManager()
        device_count = len(self.manager.devices)

        self.add_widget(Label(text=f"Gerenciador IoT Tuya v0.3", font_size='24sp'))
        self.add_widget(Label(text=f"Dispositivos encontrados: {device_count}"))

        self.btn_exit = Button(text="Sair", size_hint=(1, 0.2))
        self.btn_exit.bind(on_press=self.exit_app)
        self.add_widget(self.btn_exit)

    def exit_app(self, instance):
        App.get_running_app().stop()

class TuyaControllerApp(App):
    def build(self):
        self.title = "Controle Tuya IoT"
        return MainScreen()

if __name__ == '__main__':
    TuyaControllerApp().run()
