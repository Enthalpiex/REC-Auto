import json

class SettingsManager:
    SETTINGS_FILE = 'settings_cache.json'

    @staticmethod
    def load_settings_from_cache(ui_instance):
        try:
            with open(SettingsManager.SETTINGS_FILE, 'r') as file:
                data = json.load(file)

                ui_instance.email_entry.insert(0, data.get('email', ''))
                ui_instance.password_entry.insert(0, data.get('password', ''))

                if data.get('remember_info', False):
                    ui_instance.remember_info_var.set(True)

                    ui_instance.stay_signed_in_var.set(data.get('stay_signed_in', False))

                    selected_day = data.get('selected_day', '')
                    if selected_day:
                        ui_instance.day_combobox.set(selected_day)

                    # Add loading scheduled information
                    ui_instance.scheduled_var.set(data.get('scheduled', False))
                    ui_instance.update_scheduled_label()

        except FileNotFoundError:
            pass  # File doesn't exist, ignore
        except json.JSONDecodeError:
            print(f"Error decoding JSON in {SettingsManager.SETTINGS_FILE}")

    @staticmethod
    def save_settings_to_cache(ui_instance):
        data = {
            'email': ui_instance.email_entry.get(),
            'password': ui_instance.password_entry.get(),
            'stay_signed_in': ui_instance.stay_signed_in_var.get(),
            'remember_info': ui_instance.remember_info_var.get(),
            'selected_day': ui_instance.day_combobox.get(),
            'scheduled': ui_instance.scheduled_var.get(),
        }
        with open(SettingsManager.SETTINGS_FILE, 'w') as file:
            json.dump(data, file)
