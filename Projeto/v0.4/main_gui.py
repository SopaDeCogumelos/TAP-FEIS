"""
    Disciplina: Tópicos Avançados de Programação
    Professor: Christiane Marie Schweitzer
    Alunos: 
    - Arthur de Souza Leite
    - Luis Felipe Marcon Brunhara
    - Luiz Felipe Moura Tarifa
    Git: https://github.com/SopaDeCogumelos/TAP-FEIS

    Projeto Final - Gerenciamento de Dispositivos IoT - v0.4

    Interface Gráfica para Controle de Dispositivos IoT (Kivy)

"""

import os
import sys
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.actionbar import ActionBar, ActionView, ActionPrevious, ActionButton
from kivy.core.window import Window

# Adiciona o diretório atual ao path para garantir importação correta
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.popup import Popup
from tuya_lib import DeviceManager, SmartLamp
import tinytuya

import threading
from kivy.clock import Clock

# --- Widgets ---
class ControlScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'control'
        self.device_config = None
        self.lamp = None
        
        # Layout Principal
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Action Bar
        action_bar = ActionBar()
        av = ActionView()
        av.add_widget(ActionPrevious(title='Controle', on_press=self.go_back))
        action_bar.add_widget(av)
        self.layout.add_widget(action_bar)
        
        # Conteúdo (será preenchido dinamicamente)
        self.content_layout = BoxLayout(orientation='vertical', spacing=10)
        self.layout.add_widget(self.content_layout)
        
        self.add_widget(self.layout)

    def load_device(self, device_config):
        self.device_config = device_config
        self.lamp = SmartLamp(device_config)
        self.content_layout.clear_widgets()
        
        # Título
        self.content_layout.add_widget(Label(text=f"Controlando: {device_config['name']}", font_size='24sp', size_hint_y=None, height=50))
        
        # Status de Conexão
        self.status_label = Label(text="Conectando...", size_hint_y=None, height=30)
        self.content_layout.add_widget(self.status_label)
        
        # Switch Liga/Desliga
        power_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        power_layout.add_widget(Label(text="Energia:"))
        self.power_switch = Switch(disabled=True)
        self.power_switch.bind(active=self.toggle_power)
        power_layout.add_widget(self.power_switch)
        self.content_layout.add_widget(power_layout)
        
        # Slider Brilho
        self.content_layout.add_widget(Label(text="Brilho:", size_hint_y=None, height=30))
        self.brightness_slider = Slider(min=0, max=100, value=50, disabled=True)
        self.brightness_slider.bind(on_touch_up=self.set_brightness)
        self.content_layout.add_widget(self.brightness_slider)
        
        # Slider Temperatura
        self.content_layout.add_widget(Label(text="Temperatura:", size_hint_y=None, height=30))
        self.temp_slider = Slider(min=0, max=100, value=50, disabled=True)
        self.temp_slider.bind(on_touch_up=self.set_temperature)
        self.content_layout.add_widget(self.temp_slider)
        
        # Botão Cor
        self.btn_color = Button(text="Alterar Cor", size_hint_y=None, height=50, disabled=True)
        self.btn_color.bind(on_press=self.open_color_picker)
        self.content_layout.add_widget(self.btn_color)
        
        # Inicia conexão em thread separada
        threading.Thread(target=self.connect_device_thread, daemon=True).start()

    def connect_device_thread(self):
        """Executa a conexão em background"""
        success = self.lamp.connect()
        # Agenda atualização da UI na thread principal
        Clock.schedule_once(lambda dt: self.on_connection_result(success))

    def on_connection_result(self, success):
        """Chamado na thread principal após tentativa de conexão"""
        if success:
            self.status_label.text = "Conectado"
            self.status_label.color = (0, 1, 0, 1) # Verde
            self.enable_controls(True)
            self.update_ui_from_status()
        else:
            self.status_label.text = "Erro de Conexão (Offline)"
            self.status_label.color = (1, 0, 0, 1) # Vermelho
            self.enable_controls(False)

    def enable_controls(self, enable):
        self.power_switch.disabled = not enable
        self.brightness_slider.disabled = not enable
        self.temp_slider.disabled = not enable
        self.btn_color.disabled = not enable

    def update_ui_from_status(self):
        status = self.lamp.get_status()
        if status and 'dps' in status:
            dps = status['dps']
            # Atualiza Switch
            is_on = dps.get(self.lamp.dp_switch, False)
            # Evita disparar evento ao setar valor
            self.power_switch.unbind(active=self.toggle_power)
            self.power_switch.active = is_on
            self.power_switch.bind(active=self.toggle_power)
            
            # Atualiza Brilho (simplificado)
            # TODO: Converter escala correta
            pass

    def toggle_power(self, instance, value):
        if value:
            self.lamp.turn_on()
        else:
            self.lamp.turn_off()

    def set_brightness(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self.lamp.set_brightness(int(instance.value))

    def set_temperature(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self.lamp.set_temperature(int(instance.value))

    def open_color_picker(self, instance):
        content = BoxLayout(orientation='vertical')
        color_picker = ColorPicker()
        content.add_widget(color_picker)
        
        btn_set = Button(text="Definir Cor", size_hint_y=None, height=50)
        content.add_widget(btn_set)
        
        popup = Popup(title='Escolher Cor', content=content, size_hint=(0.9, 0.9))
        
        def set_color(inst):
            r, g, b, a = color_picker.color
            self.lamp.set_color_rgb(int(r*255), int(g*255), int(b*255))
            popup.dismiss()
            
        btn_set.bind(on_press=set_color)
        popup.open()

    def go_back(self, instance):
        self.manager.transition.direction = 'right'
        self.manager.current = 'dashboard'

class AdminScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'admin'
        
        # Layout Principal
        self.layout = BoxLayout(orientation='vertical')
        
        # Action Bar
        action_bar = ActionBar()
        av = ActionView()
        av.add_widget(ActionPrevious(title='Administração', on_press=self.go_back))
        action_bar.add_widget(av)
        self.layout.add_widget(action_bar)
        
        # Botões de Ação
        action_layout = BoxLayout(size_hint_y=None, height=60, padding=10, spacing=10)
        btn_scan = Button(text="Escanear Rede")
        btn_scan.bind(on_press=self.scan_network)
        action_layout.add_widget(btn_scan)
        
        btn_add = Button(text="Adicionar Manual")
        btn_add.bind(on_press=self.show_add_popup)
        action_layout.add_widget(btn_add)
        
        self.layout.add_widget(action_layout)
        
        # Lista de Dispositivos
        self.layout.add_widget(Label(text="Dispositivos Gerenciados:", size_hint_y=None, height=30))
        
        self.scroll = ScrollView()
        self.device_list = GridLayout(cols=1, spacing=5, size_hint_y=None, padding=10)
        self.device_list.bind(minimum_height=self.device_list.setter('height'))
        self.scroll.add_widget(self.device_list)
        self.layout.add_widget(self.scroll)
        
        self.add_widget(self.layout)

    def on_enter(self):
        self.refresh_list()

    def go_back(self, instance):
        self.manager.transition.direction = 'right'
        self.manager.current = 'dashboard'

    def refresh_list(self):
        self.device_list.clear_widgets()
        app = App.get_running_app()
        devices = app.device_manager.devices
        
        for device in devices:
            row = BoxLayout(size_hint_y=None, height=50, spacing=10)
            row.add_widget(Label(text=f"{device['name']} ({device['ip']})", size_hint_x=0.7))
            
            btn_edit = Button(text="Edit", size_hint_x=None, width=50)
            btn_edit.bind(on_press=lambda x, d=device: self.edit_device(d))
            row.add_widget(btn_edit)
            
            btn_del = Button(text="X", size_hint_x=None, width=50, background_color=(1, 0, 0, 1))
            btn_del.bind(on_press=lambda x, d=device: self.confirm_delete(d))
            row.add_widget(btn_del)
            
            self.device_list.add_widget(row)

    def edit_device(self, device):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        from kivy.uix.textinput import TextInput
        
        input_name = TextInput(text=device.get('name', ''), hint_text="Nome", multiline=False)
        input_id = TextInput(text=device.get('id', ''), hint_text="ID (Tuya)", multiline=False)
        input_key = TextInput(text=device.get('key', ''), hint_text="Local Key", multiline=False)
        input_ip = TextInput(text=device.get('ip', ''), hint_text="IP (Opcional)", multiline=False)
        input_ver = TextInput(text=device.get('version', '3.5'), hint_text="Versão (3.1, 3.3, 3.5)", multiline=False)
        
        content.add_widget(input_name)
        content.add_widget(input_id)
        content.add_widget(input_key)
        content.add_widget(input_ip)
        content.add_widget(input_ver)
        
        btn_save = Button(text="Salvar", size_hint_y=None, height=50)
        content.add_widget(btn_save)
        
        popup = Popup(title='Editar Dispositivo', content=content, size_hint=(0.9, 0.7))
        
        def save(inst):
            if not input_name.text or not input_id.text or not input_key.text:
                return 
            
            # Update existing dictionary
            device['name'] = input_name.text
            device['id'] = input_id.text
            device['key'] = input_key.text
            device['ip'] = input_ip.text
            device['version'] = input_ver.text
            
            app = App.get_running_app()
            app.device_manager.save_devices()
            self.refresh_list()
            popup.dismiss()
            
        btn_save.bind(on_press=save)
        popup.open()

    def confirm_delete(self, device):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=f"Remover {device['name']}?"))
        
        buttons = BoxLayout(size_hint_y=None, height=50, spacing=10)
        btn_yes = Button(text="Sim")
        btn_no = Button(text="Não")
        buttons.add_widget(btn_yes)
        buttons.add_widget(btn_no)
        content.add_widget(buttons)
        
        popup = Popup(title='Confirmar Exclusão', content=content, size_hint=(None, None), size=(300, 200))
        
        def delete(inst):
            app = App.get_running_app()
            app.device_manager.devices.remove(device)
            app.device_manager.save_devices()
            self.refresh_list()
            popup.dismiss()
            
        btn_yes.bind(on_press=delete)
        btn_no.bind(on_press=popup.dismiss)
        popup.open()

    def show_add_popup(self, instance):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        from kivy.uix.textinput import TextInput
        
        input_name = TextInput(hint_text="Nome", multiline=False)
        input_id = TextInput(hint_text="ID (Tuya)", multiline=False)
        input_key = TextInput(hint_text="Local Key", multiline=False)
        input_ip = TextInput(hint_text="IP (Opcional)", multiline=False)
        input_ver = TextInput(text="3.5", hint_text="Versão (3.1, 3.3, 3.5)", multiline=False)
        
        content.add_widget(input_name)
        content.add_widget(input_id)
        content.add_widget(input_key)
        content.add_widget(input_ip)
        content.add_widget(input_ver)
        
        btn_save = Button(text="Salvar", size_hint_y=None, height=50)
        content.add_widget(btn_save)
        
        popup = Popup(title='Adicionar Dispositivo', content=content, size_hint=(0.9, 0.7))
        
        def save(inst):
            if not input_name.text or not input_id.text or not input_key.text:
                return # Validação simples
            
            new_device = {
                'name': input_name.text,
                'id': input_id.text,
                'key': input_key.text,
                'ip': input_ip.text,
                'version': input_ver.text,
                'mac': '', 'uuid': '', 'model': ''
            }
            
            app = App.get_running_app()
            app.device_manager.devices.append(new_device)
            app.device_manager.save_devices()
            self.refresh_list()
            popup.dismiss()
            
        btn_save.bind(on_press=save)
        popup.open()

    def scan_network(self, instance):
        # Mostra popup de carregamento
        self.loading_popup = Popup(title='Escaneando...', content=Label(text="Aguarde..."), size_hint=(None, None), size=(200, 200), auto_dismiss=False)
        self.loading_popup.open()
        
        threading.Thread(target=self.run_scan_thread, daemon=True).start()

    def run_scan_thread(self):
        try:
            # deviceScan retorna dict com IPs como chaves
            devices = tinytuya.deviceScan(verbose=False)
            Clock.schedule_once(lambda dt: self.on_scan_complete(devices))
        except Exception as e:
            print(f"Erro no scan: {e}")
            Clock.schedule_once(lambda dt: self.on_scan_complete({}))

    def on_scan_complete(self, devices):
        self.loading_popup.dismiss()
        
        if not devices:
            popup = Popup(title='Resultado', content=Label(text="Nenhum dispositivo encontrado."), size_hint=(None, None), size=(300, 200))
            popup.open()
            return

        # Mostra lista de dispositivos encontrados para adicionar
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        scroll = ScrollView()
        grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        
        # devices é keyed por IP
        for ip, info in devices.items():
            dev_id = info.get('gwId') or info.get('id') or 'Desconhecido'
            
            row = BoxLayout(size_hint_y=None, height=80, orientation='vertical')
            row.add_widget(Label(text=f"ID: {dev_id}"))
            row.add_widget(Label(text=f"IP: {ip}"))
            
            btn_add = Button(text="Adicionar", size_hint_y=None, height=40)
            # Callback para adicionar
            btn_add.bind(on_press=lambda x, i=dev_id, inf=info: self.prompt_add_discovered(i, inf))
            row.add_widget(btn_add)
            
            grid.add_widget(row)
            
        scroll.add_widget(grid)
        content.add_widget(scroll)
        
        res_popup = Popup(title='Dispositivos Encontrados', content=content, size_hint=(0.9, 0.9))
        res_popup.open()
        self.scan_results_popup = res_popup

    def prompt_add_discovered(self, dev_id, info):
        # Fecha lista de resultados
        if hasattr(self, 'scan_results_popup'):
            self.scan_results_popup.dismiss()
            
        # Abre popup para completar dados
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        from kivy.uix.textinput import TextInput
        input_name = TextInput(hint_text="Nome", multiline=False)
        input_key = TextInput(hint_text="Local Key", multiline=False)
        
        version = info.get('version', '3.3')
        
        content.add_widget(Label(text=f"ID: {dev_id}"))
        content.add_widget(Label(text=f"IP: {info.get('ip')}"))
        content.add_widget(Label(text=f"Ver: {version}"))
        content.add_widget(input_name)
        content.add_widget(input_key)
        
        btn_save = Button(text="Salvar", size_hint_y=None, height=50)
        content.add_widget(btn_save)
        
        popup = Popup(title='Configurar Dispositivo', content=content, size_hint=(0.9, 0.6))
        
        def save(inst):
            if not input_name.text or not input_key.text:
                return
            
            new_device = {
                'name': input_name.text,
                'id': dev_id,
                'key': input_key.text,
                'ip': info.get('ip'),
                'version': version,
                'mac': info.get('mac', ''),
                'uuid': info.get('uuid', ''),
                'model': info.get('productKey', '') # productKey as model proxy
            }
            
            app = App.get_running_app()
            app.device_manager.devices.append(new_device)
            app.device_manager.save_devices()
            self.refresh_list()
            popup.dismiss()
            
        btn_save.bind(on_press=save)
        popup.open()

class DeviceCard(BoxLayout):
    def __init__(self, device, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = 150
        self.padding = 10
        self.spacing = 5
        
        # Estilo visual simples (fundo cinza escuro)
        # Em Kivy puro, precisaríamos desenhar no canvas, mas vamos manter simples por enquanto
        
        self.device = device
        
        # Nome do Dispositivo
        self.add_widget(Label(text=device.get('name', 'Desconhecido'), font_size='20sp', bold=True))
        
        # ID do Dispositivo
        self.add_widget(Label(text=f"ID: {device.get('id', 'N/A')}", font_size='14sp', color=(0.7, 0.7, 0.7, 1)))
        
        # Botão de Controle
        btn = Button(text="Controlar", size_hint_y=None, height=50)
        btn.bind(on_press=self.open_control)
        self.add_widget(btn)

    def open_control(self, instance):
        print(f"Abrindo controle para {self.device['name']}")
        # Obtém o ScreenManager através da app
        app = App.get_running_app()
        screen_manager = app.root
        
        # Obtém a tela de controle
        if 'control' in screen_manager.screen_names:
            control_screen = screen_manager.get_screen('control')
            control_screen.load_device(self.device)
            screen_manager.transition.direction = 'left'
            screen_manager.current = 'control'

class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Layout Principal
        root_layout = BoxLayout(orientation='vertical')
        
        # Action Bar (Cabeçalho)
        action_bar = ActionBar()
        av = ActionView()
        av.add_widget(ActionPrevious(title='Tuya IoT Manager', with_previous=False))
        av.add_widget(ActionButton(text='Atualizar', on_press=self.refresh_devices))
        av.add_widget(ActionButton(text='Config', on_press=self.open_settings))
        action_bar.add_widget(av)
        root_layout.add_widget(action_bar)
        
        # Lista de Dispositivos com Scroll
        scroll = ScrollView()
        self.device_grid = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=10)
        self.device_grid.bind(minimum_height=self.device_grid.setter('height'))
        
        scroll.add_widget(self.device_grid)
        root_layout.add_widget(scroll)
        
        self.add_widget(root_layout)
        
        # Inicializa lista (o manager está na App)
        # self.refresh_devices() será chamado no on_enter ou manualmente
        Clock.schedule_once(self.refresh_devices)

    def refresh_devices(self, instance=None):
        self.device_grid.clear_widgets()
        app = App.get_running_app()
        app.device_manager.load_devices() # Recarrega do arquivo
        
        if not app.device_manager.devices:
            self.device_grid.add_widget(Label(text="Nenhum dispositivo encontrado.\nVá em Config > Wizard.", size_hint_y=None, height=100))
            return

        for device in app.device_manager.devices:
            card = DeviceCard(device=device)
            self.device_grid.add_widget(card)

    def open_settings(self, instance):
        self.manager.transition.direction = 'left'
        self.manager.current = 'admin'

class TuyaControllerApp(App):
    def build(self):
        self.title = "Projeto JarVision v0.4"
        self.device_manager = DeviceManager()
        
        sm = ScreenManager()
        self.dashboard = DashboardScreen(name='dashboard')
        self.control = ControlScreen(name='control')
        self.admin = AdminScreen(name='admin')
        
        sm.add_widget(self.dashboard)
        sm.add_widget(self.control)
        sm.add_widget(self.admin)
        return sm

if __name__ == '__main__':
    TuyaControllerApp().run()
