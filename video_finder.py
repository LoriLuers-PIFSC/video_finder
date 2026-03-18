import os
import csv
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from hachoir.core import config

# Suppress hachoir internal warnings
config.quiet = True

def get_video_info(path):
    """Extracts orientation and resolution using Hachoir."""
    try:
        parser = createParser(path)
        if not parser:
            return "Unknown", "N/A"
            
        with parser:
            metadata = extractMetadata(parser)
            if metadata:
                width = metadata.get('width')
                height = metadata.get('height')
                if width and height:
                    orientation = "Horizontal" if width > height else "Vertical"
                    res = f"{width}x{height}"
                    return orientation, res
    except Exception:
        pass
    return "Unknown", "N/A"

def browse_folder():
    selected_path = filedialog.askdirectory()
    if selected_path:
        entry_path.delete(0, tk.END)
        entry_path.insert(0, selected_path)

def run_search():
    path = entry_path.get()
    if not path or not os.path.exists(path):
        messagebox.showwarning("Error", "Please select a valid directory.")
        return

    # Clear previous results
    text_results.delete(1.0, tk.END)
    video_extensions = ('.mp4', '.mkv', '.mov', '.avi', '.wmv', '.flv', '.webm', '.m4v')
    
    # Header for the UI Display
    header = f"{'FILE NAME':<40} | {'ORIENTATION':<15} | {'RES':<12} | {'LOCATION'}\n"
    text_results.insert(tk.END, header)
    text_results.insert(tk.END, "-" * 130 + "\n")
    root.update_idletasks()

    found_count = 0
    for root_dir, _, files in os.walk(path):
        for file in files:
            if file.lower().endswith(video_extensions):
                full_path = os.path.join(root_dir, file)
                
                # Fetch Metadata
                orientation, resolution = get_video_info(full_path)
                
                # Format line for display (shortening filename if too long for UI)
                display_name = (file[:37] + '..') if len(file) > 39 else file
                result_line = f"{display_name:<40} | {orientation:<15} | {resolution:<12} | {full_path}\n"
                
                text_results.insert(tk.END, result_line)
                text_results.see(tk.END) # Scroll as we find things
                root.update_idletasks() # Keep window responsive
                found_count += 1

    messagebox.showinfo("Done", f"Search complete! Found {found_count} videos.")

def export_to_csv():
    # Grab data from the text widget
    content = text_results.get(1.0, tk.END).strip().split('\n')
    
    if len(content) < 3: # Header + Separator + Data
        messagebox.showwarning("Empty", "No data to export! Run a search first.")
        return
        
    save_path = filedialog.asksaveasfilename(defaultextension=".csv", 
                                            filetypes=[("CSV files", "*.csv")])
    if save_path:
        try:
            with open(save_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                # Write CSV Headers
                writer.writerow(["File Name", "Orientation", "Resolution", "Full Path"])
                
                # Parse the display text back into CSV rows
                # content[0] is header, content[1] is dashes, content[2:] is data
                for line in content[2:]:
                    if "|" in line:
                        parts = [p.strip() for p in line.split("|")]
                        writer.writerow(parts)
                        
            messagebox.showinfo("Success", f"File saved to:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Could not save file: {e}")

# --- UI Layout ---
root = tk.Tk()
root.title("Video Asset Manager v1.0")
root.geometry("1200x700")

# Top Control Frame
top_frame = tk.Frame(root, padx=15, pady=15)
top_frame.pack(fill=tk.X)

tk.Label(top_frame, text="Select Folder:", font=('Segoe UI', 10)).pack(side=tk.LEFT)
entry_path = tk.Entry(top_frame, width=60, font=('Segoe UI', 10))
entry_path.pack(side=tk.LEFT, padx=10)

tk.Button(top_frame, text="Browse", command=browse_folder, width=10).pack(side=tk.LEFT)

# Action Buttons
btn_run = tk.Button(top_frame, text="RUN SEARCH", command=run_search, 
                   bg="#2ecc71", fg="white", font=('Segoe UI', 10, 'bold'), width=15)
btn_run.pack(side=tk.LEFT, padx=(20, 5))

btn_export = tk.Button(top_frame, text="EXPORT CSV", command=export_to_csv, 
                      bg="#3498db", fg="white", font=('Segoe UI', 10), width=15)
btn_export.pack(side=tk.LEFT)

# Results Display Area
text_results = scrolledtext.ScrolledText(root, width=140, height=35, 
                                        font=("Consolas", 10), bg="#f8f9fa")
text_results.pack(padx=15, pady=10, fill=tk.BOTH, expand=True)

root.mainloop()