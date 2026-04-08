from core.setup_wizard import SetupWizard
from gui.app import App

if __name__ == "__main__":
    # Run setup wizard on first launch
    wizard = SetupWizard()
    if wizard.is_first_run():
        wizard.run_setup()
    
    app = App()
    app.mainloop()