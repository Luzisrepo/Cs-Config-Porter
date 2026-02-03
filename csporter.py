import os
import sys
import shutil
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from pathlib import Path

class CSGOSettingsPorter:
    def __init__(self, root):
        self.root = root
        self.root.title("CS:GO/CS2 Settings Porter")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Set application icon (if available)
        try:
            self.root.iconbitmap("csgo_icon.ico")
        except:
            pass
        
        # Define colors
        self.primary_color = "#1e3a8a"  # Dark blue
        self.secondary_color = "#3b82f6"  # Blue
        self.accent_color = "#10b981"  # Green
        self.warning_color = "#ef4444"  # Red
        
        # Steam paths
        self.steam_path_default = r"C:\Program Files (x86)\Steam\userdata"
        self.cfg_path = r"730\local\cfg"
        self.backup_dir_default = r"C:\Program Files (x86)\Steam\cs_backups"
        
        # Initialize variables
        self.steam_path = self.steam_path_default
        self.backup_dir = self.backup_dir_default
        self.accounts = []
        
        # Create GUI
        self.setup_ui()
        
        # Check if Steam path exists
        self.check_steam_path()
        
        # Load accounts on startup
        self.load_accounts()
    
    def setup_ui(self):
        # Apply modern theme styling first
        self.apply_styling()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create frames for each tab
        self.main_frame = ttk.Frame(self.notebook)
        self.port_frame = ttk.Frame(self.notebook)
        self.backup_frame = ttk.Frame(self.notebook)
        self.restore_frame = ttk.Frame(self.notebook)
        self.settings_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.main_frame, text="Dashboard")
        self.notebook.add(self.port_frame, text="Port Settings")
        self.notebook.add(self.backup_frame, text="Backup")
        self.notebook.add(self.restore_frame, text="Restore")
        self.notebook.add(self.settings_frame, text="Settings")
        
        # Setup each tab
        self.setup_dashboard_tab()
        self.setup_port_tab()
        self.setup_backup_tab()
        self.setup_restore_tab()
        self.setup_settings_tab()
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 10))
    
    def apply_styling(self):
        # Configure colors and fonts
        self.root.configure(bg="#f0f0f0")
        
        # Create style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure button styles
        style.configure('Primary.TButton', foreground='white', background=self.primary_color, 
                       borderwidth=1, focusthickness=3, focuscolor='none')
        style.map('Primary.TButton', background=[('active', self.secondary_color)])
        
        style.configure('Success.TButton', foreground='white', background=self.accent_color)
        style.map('Success.TButton', background=[('active', '#0da271')])
        
        style.configure('Danger.TButton', foreground='white', background=self.warning_color)
        style.map('Danger.TButton', background=[('active', '#dc2626')])
        
        # Configure label styles
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), foreground=self.primary_color)
        style.configure('Subtitle.TLabel', font=('Segoe UI', 12), foreground='#4b5563')
        
        # Configure entry styles
        style.configure('Custom.TEntry', fieldbackground='white', borderwidth=1, relief='solid')
    
    def setup_dashboard_tab(self):
        # Header
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        title_label = ttk.Label(header_frame, text="CS:GO/CS2 Settings Porter", style='Title.TLabel')
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(header_frame, 
                                  text="Manage and transfer your CS:GO/CS2 settings between Steam accounts", 
                                  style='Subtitle.TLabel')
        subtitle_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Stats frame
        stats_frame = ttk.LabelFrame(self.main_frame, text="Statistics", padding=15)
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)
        
        # Account count
        self.account_count_var = tk.StringVar(value="0")
        account_count_frame = ttk.Frame(stats_grid)
        account_count_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Label(account_count_frame, text="Accounts Found:", font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W)
        ttk.Label(account_count_frame, textvariable=self.account_count_var, 
                 font=('Segoe UI', 24, 'bold'), foreground=self.primary_color).pack(anchor=tk.W)
        
        # Steam path status
        steam_status_frame = ttk.Frame(stats_grid)
        steam_status_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(steam_status_frame, text="Steam Path:", font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W)
        steam_path_label = ttk.Label(steam_status_frame, text=self.steam_path, 
                                    font=('Segoe UI', 9), foreground='#6b7280', wraplength=300)
        steam_path_label.pack(anchor=tk.W)
        
        # Quick actions frame
        actions_frame = ttk.LabelFrame(self.main_frame, text="Quick Actions", padding=15)
        actions_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Action buttons grid
        button_grid = ttk.Frame(actions_frame)
        button_grid.pack(fill=tk.BOTH, expand=True)
        
        # Reload accounts button
        reload_btn = ttk.Button(button_grid, text="⟳ Reload Accounts", 
                               command=self.load_accounts, style='Primary.TButton')
        reload_btn.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NSEW)
        
        # Port settings button
        port_btn = ttk.Button(button_grid, text="⚡ Port Settings", 
                             command=lambda: self.notebook.select(self.port_frame), style='Primary.TButton')
        port_btn.grid(row=0, column=1, padx=5, pady=5, sticky=tk.NSEW)
        
        # Create backup button
        backup_btn = ttk.Button(button_grid, text="📁 Create Backup", 
                               command=lambda: self.notebook.select(self.backup_frame), style='Success.TButton')
        backup_btn.grid(row=1, column=0, padx=5, pady=5, sticky=tk.NSEW)
        
        # Restore backup button
        restore_btn = ttk.Button(button_grid, text="↩ Restore Backup", 
                                command=lambda: self.notebook.select(self.restore_frame), style='Success.TButton')
        restore_btn.grid(row=1, column=1, padx=5, pady=5, sticky=tk.NSEW)
        
        # Accounts list frame
        list_frame = ttk.LabelFrame(self.main_frame, text="Detected Steam Accounts", padding=15)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Listbox with scrollbar
        listbox_frame = ttk.Frame(list_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.accounts_listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, 
                                          font=('Consolas', 10), height=8)
        self.accounts_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.accounts_listbox.yview)
    
    def setup_port_tab(self):
        # Header
        header_frame = ttk.Frame(self.port_frame)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        title_label = ttk.Label(header_frame, text="Port Settings Between Accounts", style='Title.TLabel')
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(header_frame, 
                                  text="Copy CS:GO/CS2 settings from one Steam account to another", 
                                  style='Subtitle.TLabel')
        subtitle_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Form frame
        form_frame = ttk.Frame(self.port_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Source account
        source_frame = ttk.LabelFrame(form_frame, text="Source Account", padding=15)
        source_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(source_frame, text="Select or enter the source account ID:").pack(anchor=tk.W, pady=(0, 5))
        
        source_input_frame = ttk.Frame(source_frame)
        source_input_frame.pack(fill=tk.X)
        
        self.source_account_var = tk.StringVar()
        self.source_account_entry = ttk.Entry(source_input_frame, textvariable=self.source_account_var, 
                                             style='Custom.TEntry', font=('Segoe UI', 10))
        self.source_account_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        source_list_btn = ttk.Button(source_input_frame, text="Browse Accounts", 
                                    command=self.show_accounts_dialog, style='Primary.TButton')
        source_list_btn.pack(side=tk.RIGHT)
        
        # Target account
        target_frame = ttk.LabelFrame(form_frame, text="Target Account", padding=15)
        target_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(target_frame, text="Select or enter the target account ID:").pack(anchor=tk.W, pady=(0, 5))
        
        target_input_frame = ttk.Frame(target_frame)
        target_input_frame.pack(fill=tk.X)
        
        self.target_account_var = tk.StringVar()
        self.target_account_entry = ttk.Entry(target_input_frame, textvariable=self.target_account_var, 
                                             style='Custom.TEntry', font=('Segoe UI', 10))
        self.target_account_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        target_list_btn = ttk.Button(target_input_frame, text="Browse Accounts", 
                                    command=lambda: self.show_accounts_dialog(target=True), style='Primary.TButton')
        target_list_btn.pack(side=tk.RIGHT)
        
        # Options frame
        options_frame = ttk.LabelFrame(form_frame, text="Options", padding=15)
        options_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.create_backup_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Create backup of target account before porting", 
                       variable=self.create_backup_var).pack(anchor=tk.W)
        
        # Action buttons
        action_frame = ttk.Frame(form_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        port_btn = ttk.Button(action_frame, text="🚀 Port Settings", 
                             command=self.port_settings, style='Success.TButton', width=20)
        port_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = ttk.Button(action_frame, text="Clear", 
                              command=self.clear_port_form, style='Danger.TButton')
        clear_btn.pack(side=tk.LEFT)
        
        # Progress bar
        self.port_progress = ttk.Progressbar(form_frame, mode='indeterminate')
        self.port_progress.pack(fill=tk.X, pady=(10, 0))
        
        # Log output
        log_frame = ttk.LabelFrame(form_frame, text="Operation Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.port_log_text = tk.Text(log_frame, height=8, font=('Consolas', 9), wrap=tk.WORD)
        self.port_log_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.port_log_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.port_log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.port_log_text.yview)
    
    def setup_backup_tab(self):
        # Header
        header_frame = ttk.Frame(self.backup_frame)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        title_label = ttk.Label(header_frame, text="Create Backup", style='Title.TLabel')
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(header_frame, 
                                  text="Back up CS:GO/CS2 settings for a Steam account", 
                                  style='Subtitle.TLabel')
        subtitle_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Form frame
        form_frame = ttk.Frame(self.backup_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Account selection
        account_frame = ttk.LabelFrame(form_frame, text="Account Selection", padding=15)
        account_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(account_frame, text="Select or enter the account ID to backup:").pack(anchor=tk.W, pady=(0, 5))
        
        account_input_frame = ttk.Frame(account_frame)
        account_input_frame.pack(fill=tk.X)
        
        self.backup_account_var = tk.StringVar()
        self.backup_account_entry = ttk.Entry(account_input_frame, textvariable=self.backup_account_var, 
                                             style='Custom.TEntry', font=('Segoe UI', 10))
        self.backup_account_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        backup_list_btn = ttk.Button(account_input_frame, text="Browse Accounts", 
                                    command=lambda: self.show_accounts_dialog(backup=True), style='Primary.TButton')
        backup_list_btn.pack(side=tk.RIGHT)
        
        # Backup location
        location_frame = ttk.LabelFrame(form_frame, text="Backup Location", padding=15)
        location_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(location_frame, text="Select backup directory:").pack(anchor=tk.W, pady=(0, 5))
        
        location_input_frame = ttk.Frame(location_frame)
        location_input_frame.pack(fill=tk.X)
        
        self.backup_location_var = tk.StringVar(value=self.backup_dir)
        self.backup_location_entry = ttk.Entry(location_input_frame, textvariable=self.backup_location_var, 
                                              style='Custom.TEntry', font=('Segoe UI', 10))
        self.backup_location_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(location_input_frame, text="Browse", 
                               command=self.browse_backup_location, style='Primary.TButton')
        browse_btn.pack(side=tk.RIGHT)
        
        # Action buttons
        action_frame = ttk.Frame(form_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        backup_btn = ttk.Button(action_frame, text="💾 Create Backup", 
                               command=self.create_backup, style='Success.TButton', width=20)
        backup_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = ttk.Button(action_frame, text="Clear", 
                              command=self.clear_backup_form, style='Danger.TButton')
        clear_btn.pack(side=tk.LEFT)
        
        # Progress bar
        self.backup_progress = ttk.Progressbar(form_frame, mode='indeterminate')
        self.backup_progress.pack(fill=tk.X, pady=(10, 0))
        
        # Log output
        log_frame = ttk.LabelFrame(form_frame, text="Operation Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.backup_log_text = tk.Text(log_frame, height=8, font=('Consolas', 9), wrap=tk.WORD)
        self.backup_log_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.backup_log_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.backup_log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.backup_log_text.yview)
    
    def setup_restore_tab(self):
        # Header
        header_frame = ttk.Frame(self.restore_frame)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        title_label = ttk.Label(header_frame, text="Restore Backup", style='Title.TLabel')
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(header_frame, 
                                  text="Restore a previously created backup to a Steam account", 
                                  style='Subtitle.TLabel')
        subtitle_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Form frame
        form_frame = ttk.Frame(self.restore_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Backup selection
        backup_frame = ttk.LabelFrame(form_frame, text="Backup Selection", padding=15)
        backup_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(backup_frame, text="Select a backup to restore:").pack(anchor=tk.W, pady=(0, 5))
        
        backup_input_frame = ttk.Frame(backup_frame)
        backup_input_frame.pack(fill=tk.X)
        
        self.backup_name_var = tk.StringVar()
        self.backup_combobox = ttk.Combobox(backup_input_frame, textvariable=self.backup_name_var, 
                                           state="readonly", font=('Segoe UI', 10))
        self.backup_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        refresh_btn = ttk.Button(backup_input_frame, text="Refresh", 
                                command=self.load_backups, style='Primary.TButton')
        refresh_btn.pack(side=tk.RIGHT)
        
        # Target account
        target_frame = ttk.LabelFrame(form_frame, text="Target Account", padding=15)
        target_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(target_frame, text="Select or enter the target account ID:").pack(anchor=tk.W, pady=(0, 5))
        
        target_input_frame = ttk.Frame(target_frame)
        target_input_frame.pack(fill=tk.X)
        
        self.restore_target_var = tk.StringVar()
        self.restore_target_entry = ttk.Entry(target_input_frame, textvariable=self.restore_target_var, 
                                             style='Custom.TEntry', font=('Segoe UI', 10))
        self.restore_target_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        target_list_btn = ttk.Button(target_input_frame, text="Browse Accounts", 
                                    command=lambda: self.show_accounts_dialog(restore=True), style='Primary.TButton')
        target_list_btn.pack(side=tk.RIGHT)
        
        # Action buttons
        action_frame = ttk.Frame(form_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        restore_btn = ttk.Button(action_frame, text="↩ Restore Backup", 
                                command=self.restore_backup, style='Success.TButton', width=20)
        restore_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = ttk.Button(action_frame, text="Clear", 
                              command=self.clear_restore_form, style='Danger.TButton')
        clear_btn.pack(side=tk.LEFT)
        
        # Progress bar
        self.restore_progress = ttk.Progressbar(form_frame, mode='indeterminate')
        self.restore_progress.pack(fill=tk.X, pady=(10, 0))
        
        # Log output
        log_frame = ttk.LabelFrame(form_frame, text="Operation Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.restore_log_text = tk.Text(log_frame, height=8, font=('Consolas', 9), wrap=tk.WORD)
        self.restore_log_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.restore_log_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.restore_log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.restore_log_text.yview)
        
        # Load backups on tab show
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
    
    def setup_settings_tab(self):
        # Header
        header_frame = ttk.Frame(self.settings_frame)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        title_label = ttk.Label(header_frame, text="Application Settings", style='Title.TLabel')
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(header_frame, 
                                  text="Configure application paths and preferences", 
                                  style='Subtitle.TLabel')
        subtitle_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Settings form
        form_frame = ttk.Frame(self.settings_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Steam path setting
        steam_frame = ttk.LabelFrame(form_frame, text="Steam Installation Path", padding=15)
        steam_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(steam_frame, text="Path to Steam userdata folder:").pack(anchor=tk.W, pady=(0, 5))
        
        steam_input_frame = ttk.Frame(steam_frame)
        steam_input_frame.pack(fill=tk.X)
        
        self.steam_path_var = tk.StringVar(value=self.steam_path)
        self.steam_path_entry = ttk.Entry(steam_input_frame, textvariable=self.steam_path_var, 
                                         style='Custom.TEntry', font=('Segoe UI', 10))
        self.steam_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        steam_browse_btn = ttk.Button(steam_input_frame, text="Browse", 
                                     command=self.browse_steam_path, style='Primary.TButton')
        steam_browse_btn.pack(side=tk.RIGHT)
        
        # Backup path setting
        backup_frame = ttk.LabelFrame(form_frame, text="Backup Directory", padding=15)
        backup_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(backup_frame, text="Path to backup folder:").pack(anchor=tk.W, pady=(0, 5))
        
        backup_input_frame = ttk.Frame(backup_frame)
        backup_input_frame.pack(fill=tk.X)
        
        self.settings_backup_var = tk.StringVar(value=self.backup_dir)
        self.settings_backup_entry = ttk.Entry(backup_input_frame, textvariable=self.settings_backup_var, 
                                              style='Custom.TEntry', font=('Segoe UI', 10))
        self.settings_backup_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        backup_browse_btn = ttk.Button(backup_input_frame, text="Browse", 
                                      command=self.browse_settings_backup, style='Primary.TButton')
        backup_browse_btn.pack(side=tk.RIGHT)
        
        # Action buttons
        action_frame = ttk.Frame(form_frame)
        action_frame.pack(fill=tk.X, pady=20)
        
        save_btn = ttk.Button(action_frame, text="💾 Save Settings", 
                             command=self.save_settings, style='Success.TButton', width=20)
        save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        reset_btn = ttk.Button(action_frame, text="Reset to Defaults", 
                              command=self.reset_settings, style='Danger.TButton')
        reset_btn.pack(side=tk.LEFT)
        
        # Status message
        self.settings_status_label = ttk.Label(form_frame, text="", foreground=self.accent_color)
        self.settings_status_label.pack(anchor=tk.W)
        
        # Info frame
        info_frame = ttk.LabelFrame(form_frame, text="Information", padding=15)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        info_text = """
CS:GO/CS2 Settings Porter
        
This application allows you to:
1. Port CS:GO/CS2 settings between Steam accounts
2. Create backups of your settings
3. Restore settings from backups
        
Note: You may need to restart CS:GO/CS2 for changes to take effect.
        """
        
        info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT)
        info_label.pack(anchor=tk.W)
    
    def check_steam_path(self):
        """Check if Steam path exists and update status"""
        if os.path.exists(self.steam_path):
            self.status_bar.config(text=f"Steam path found: {self.steam_path}")
            return True
        else:
            self.status_bar.config(text=f"Steam path not found: {self.steam_path}")
            messagebox.showwarning("Steam Path Not Found", 
                                  f"The Steam path was not found at:\n{self.steam_path}\n\nPlease update the path in the Settings tab.")
            return False
    
    def load_accounts(self):
        """Load Steam accounts with CS configs"""
        self.accounts = []
        self.accounts_listbox.delete(0, tk.END)
        
        if not self.check_steam_path():
            self.account_count_var.set("0")
            return
        
        try:
            # List directories in Steam path that are numeric (Steam IDs)
            for item in os.listdir(self.steam_path):
                item_path = os.path.join(self.steam_path, item)
                if os.path.isdir(item_path) and item.isdigit():
                    cfg_path = os.path.join(item_path, self.cfg_path)
                    if os.path.exists(cfg_path):
                        self.accounts.append(item)
                        self.accounts_listbox.insert(tk.END, f"{item} (Has CS config)")
                    else:
                        self.accounts_listbox.insert(tk.END, f"{item} (No CS config)")
            
            self.account_count_var.set(str(len(self.accounts)))
            self.status_bar.config(text=f"Found {len(self.accounts)} Steam accounts with CS configs")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load accounts: {str(e)}")
            self.status_bar.config(text="Error loading accounts")
    
    def show_accounts_dialog(self, target=False, backup=False, restore=False):
        """Show dialog to select an account"""
        if not self.accounts:
            messagebox.showinfo("No Accounts", "No Steam accounts with CS configs found.")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Steam Account")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Listbox with scrollbar
        listbox_frame = ttk.Frame(dialog, padding=10)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        accounts_list = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, 
                                  font=('Consolas', 10), selectmode=tk.SINGLE)
        accounts_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=accounts_list.yview)
        
        # Populate listbox
        for account in self.accounts:
            accounts_list.insert(tk.END, account)
        
        # Selection button
        def select_account():
            selection = accounts_list.curselection()
            if selection:
                account_id = accounts_list.get(selection[0])
                if target:
                    self.target_account_var.set(account_id)
                elif backup:
                    self.backup_account_var.set(account_id)
                elif restore:
                    self.restore_target_var.set(account_id)
                else:
                    self.source_account_var.set(account_id)
                dialog.destroy()
        
        button_frame = ttk.Frame(dialog, padding=10)
        button_frame.pack(fill=tk.X)
        
        select_btn = ttk.Button(button_frame, text="Select", command=select_account, style='Primary.TButton')
        select_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=dialog.destroy)
        cancel_btn.pack(side=tk.RIGHT)
    
    def port_settings(self):
        """Port settings from source to target account"""
        source_id = self.source_account_var.get().strip()
        target_id = self.target_account_var.get().strip()
        
        # Validate inputs
        if not source_id or not target_id:
            messagebox.showwarning("Missing Information", "Please enter both source and target account IDs.")
            return
        
        if source_id == target_id:
            messagebox.showwarning("Same Accounts", "Source and target accounts cannot be the same.")
            return
        
        # Validate paths
        source_path = os.path.join(self.steam_path, source_id, self.cfg_path)
        if not os.path.exists(source_path):
            messagebox.showerror("Source Not Found", f"Source account not found or doesn't have CS configs: {source_id}")
            return
        
        # Start operation in thread
        self.port_progress.start()
        self.port_log_text.delete(1.0, tk.END)
        self.port_log_text.insert(tk.END, f"Starting port operation...\n")
        self.port_log_text.insert(tk.END, f"Source: {source_id}\n")
        self.port_log_text.insert(tk.END, f"Target: {target_id}\n")
        self.port_log_text.see(tk.END)
        
        threading.Thread(target=self._port_settings_thread, 
                        args=(source_id, target_id, source_path), daemon=True).start()
    
    def _port_settings_thread(self, source_id, target_id, source_path):
        """Thread function for porting settings"""
        try:
            # Create target directories if they don't exist
            target_path = os.path.join(self.steam_path, target_id, self.cfg_path)
            os.makedirs(target_path, exist_ok=True)
            
            # Create backup of target if option is enabled
            if self.create_backup_var.get():
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                backup_path = os.path.join(self.steam_path, target_id, f"{self.cfg_path}_backup_{timestamp}")
                
                self.root.after(0, self._update_port_log, f"Creating backup of target account...\n")
                if os.path.exists(target_path) and os.listdir(target_path):
                    shutil.copytree(target_path, backup_path, dirs_exist_ok=True)
                    self.root.after(0, self._update_port_log, f"Backup created at: {backup_path}\n")
            
            # Copy files from source to target
            self.root.after(0, self._update_port_log, "Copying config files...\n")
            
            # Clear target directory
            for item in os.listdir(target_path):
                item_path = os.path.join(target_path, item)
                if os.path.isfile(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            
            # Copy source files
            for item in os.listdir(source_path):
                s = os.path.join(source_path, item)
                d = os.path.join(target_path, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)
            
            # Update UI
            self.root.after(0, self._update_port_log, f"✓ Settings successfully copied from {source_id} to {target_id}\n")
            self.root.after(0, self._update_port_log, "\nNote: You may need to restart CS:GO/CS2 for changes to take effect.\n")
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Settings successfully copied from {source_id} to {target_id}"))
            
        except Exception as e:
            self.root.after(0, self._update_port_log, f"✗ Error: {str(e)}\n")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to port settings: {str(e)}"))
        
        finally:
            self.root.after(0, self.port_progress.stop)
    
    def _update_port_log(self, message):
        """Update port log text"""
        self.port_log_text.insert(tk.END, message)
        self.port_log_text.see(tk.END)
    
    def create_backup(self):
        """Create backup of account settings"""
        account_id = self.backup_account_var.get().strip()
        backup_dir = self.backup_location_var.get().strip()
        
        # Validate inputs
        if not account_id:
            messagebox.showwarning("Missing Information", "Please enter an account ID.")
            return
        
        # Validate account path
        account_path = os.path.join(self.steam_path, account_id, self.cfg_path)
        if not os.path.exists(account_path):
            messagebox.showerror("Account Not Found", f"Account not found or doesn't have CS configs: {account_id}")
            return
        
        # Create backup directory if it doesn't exist
        os.makedirs(backup_dir, exist_ok=True)
        
        # Start operation in thread
        self.backup_progress.start()
        self.backup_log_text.delete(1.0, tk.END)
        self.backup_log_text.insert(tk.END, f"Starting backup operation...\n")
        self.backup_log_text.insert(tk.END, f"Account: {account_id}\n")
        self.backup_log_text.insert(tk.END, f"Backup location: {backup_dir}\n")
        self.backup_log_text.see(tk.END)
        
        threading.Thread(target=self._create_backup_thread, 
                        args=(account_id, account_path, backup_dir), daemon=True).start()
    
    def _create_backup_thread(self, account_id, account_path, backup_dir):
        """Thread function for creating backup"""
        try:
            # Create backup with timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            backup_name = f"{account_id}_{timestamp}"
            backup_path = os.path.join(backup_dir, backup_name)
            
            self.root.after(0, self._update_backup_log, f"Creating backup: {backup_name}\n")
            
            # Copy files
            shutil.copytree(account_path, backup_path)
            
            # Update UI
            self.root.after(0, self._update_backup_log, f"✓ Backup created successfully!\n")
            self.root.after(0, self._update_backup_log, f"Location: {backup_path}\n")
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Backup created successfully!\n\nLocation: {backup_path}"))
            
        except Exception as e:
            self.root.after(0, self._update_backup_log, f"✗ Error: {str(e)}\n")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to create backup: {str(e)}"))
        
        finally:
            self.root.after(0, self.backup_progress.stop)
            self.root.after(0, self.load_backups)  # Refresh backup list
    
    def _update_backup_log(self, message):
        """Update backup log text"""
        self.backup_log_text.insert(tk.END, message)
        self.backup_log_text.see(tk.END)
    
    def load_backups(self):
        """Load available backups"""
        backup_dir = self.backup_location_var.get().strip()
        
        if not os.path.exists(backup_dir):
            self.backup_combobox['values'] = []
            return
        
        try:
            backups = []
            for item in os.listdir(backup_dir):
                item_path = os.path.join(backup_dir, item)
                if os.path.isdir(item_path):
                    backups.append(item)
            
            self.backup_combobox['values'] = backups
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load backups: {str(e)}")
    
    def restore_backup(self):
        """Restore backup to account"""
        backup_name = self.backup_name_var.get().strip()
        target_id = self.restore_target_var.get().strip()
        
        # Validate inputs
        if not backup_name or not target_id:
            messagebox.showwarning("Missing Information", "Please select a backup and enter a target account ID.")
            return
        
        # Validate paths
        backup_dir = self.backup_location_var.get().strip()
        backup_path = os.path.join(backup_dir, backup_name)
        
        if not os.path.exists(backup_path):
            messagebox.showerror("Backup Not Found", f"Backup not found: {backup_name}")
            return
        
        # Start operation in thread
        self.restore_progress.start()
        self.restore_log_text.delete(1.0, tk.END)
        self.restore_log_text.insert(tk.END, f"Starting restore operation...\n")
        self.restore_log_text.insert(tk.END, f"Backup: {backup_name}\n")
        self.restore_log_text.insert(tk.END, f"Target account: {target_id}\n")
        self.restore_log_text.see(tk.END)
        
        threading.Thread(target=self._restore_backup_thread, 
                        args=(backup_name, backup_path, target_id), daemon=True).start()
    
    def _restore_backup_thread(self, backup_name, backup_path, target_id):
        """Thread function for restoring backup"""
        try:
            # Create target directory if it doesn't exist
            target_path = os.path.join(self.steam_path, target_id, self.cfg_path)
            os.makedirs(target_path, exist_ok=True)
            
            # Clear target directory
            self.root.after(0, self._update_restore_log, "Clearing target directory...\n")
            for item in os.listdir(target_path):
                item_path = os.path.join(target_path, item)
                if os.path.isfile(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            
            # Copy backup files
            self.root.after(0, self._update_restore_log, "Restoring backup files...\n")
            for item in os.listdir(backup_path):
                s = os.path.join(backup_path, item)
                d = os.path.join(target_path, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)
            
            # Update UI
            self.root.after(0, self._update_restore_log, f"✓ Backup successfully restored to account {target_id}\n")
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Backup successfully restored to account {target_id}"))
            
        except Exception as e:
            self.root.after(0, self._update_restore_log, f"✗ Error: {str(e)}\n")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to restore backup: {str(e)}"))
        
        finally:
            self.root.after(0, self.restore_progress.stop)
    
    def _update_restore_log(self, message):
        """Update restore log text"""
        self.restore_log_text.insert(tk.END, message)
        self.restore_log_text.see(tk.END)
    
    def browse_steam_path(self):
        """Browse for Steam path"""
        path = filedialog.askdirectory(title="Select Steam userdata folder", 
                                      initialdir=self.steam_path)
        if path:
            self.steam_path_var.set(path)
    
    def browse_backup_location(self):
        """Browse for backup location"""
        path = filedialog.askdirectory(title="Select backup directory", 
                                      initialdir=self.backup_dir)
        if path:
            self.backup_location_var.set(path)
    
    def browse_settings_backup(self):
        """Browse for backup location in settings tab"""
        path = filedialog.askdirectory(title="Select backup directory", 
                                      initialdir=self.backup_dir)
        if path:
            self.settings_backup_var.set(path)
    
    def save_settings(self):
        """Save application settings"""
        new_steam_path = self.steam_path_var.get().strip()
        new_backup_dir = self.settings_backup_var.get().strip()
        
        # Validate Steam path
        if not os.path.exists(new_steam_path):
            messagebox.showerror("Invalid Path", f"Steam path not found: {new_steam_path}")
            return
        
        # Update settings
        self.steam_path = new_steam_path
        self.backup_dir = new_backup_dir
        self.backup_location_var.set(new_backup_dir)
        
        # Update status
        self.settings_status_label.config(text="✓ Settings saved successfully")
        self.root.after(3000, lambda: self.settings_status_label.config(text=""))
        
        # Reload accounts
        self.load_accounts()
        
        # Reload backups
        self.load_backups()
        
        self.status_bar.config(text=f"Settings saved. Steam path: {self.steam_path}")
    
    def reset_settings(self):
        """Reset settings to defaults"""
        self.steam_path_var.set(self.steam_path_default)
        self.settings_backup_var.set(self.backup_dir_default)
        self.settings_status_label.config(text="✓ Settings reset to defaults")
        self.root.after(3000, lambda: self.settings_status_label.config(text=""))
    
    def clear_port_form(self):
        """Clear port form fields"""
        self.source_account_var.set("")
        self.target_account_var.set("")
        self.port_log_text.delete(1.0, tk.END)
    
    def clear_backup_form(self):
        """Clear backup form fields"""
        self.backup_account_var.set("")
        self.backup_log_text.delete(1.0, tk.END)
    
    def clear_restore_form(self):
        """Clear restore form fields"""
        self.backup_name_var.set("")
        self.restore_target_var.set("")
        self.restore_log_text.delete(1.0, tk.END)
    
    def on_tab_changed(self, event):
        """Handle tab change event"""
        selected_tab = self.notebook.index(self.notebook.select())
        
        if selected_tab == 3:  # Restore tab
            self.load_backups()
        elif selected_tab == 0:  # Dashboard tab
            self.load_accounts()

def main():
    root = tk.Tk()
    app = CSGOSettingsPorter(root)
    
    # Center window on screen
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = root.winfo_width()
    window_height = root.winfo_height()
    
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()