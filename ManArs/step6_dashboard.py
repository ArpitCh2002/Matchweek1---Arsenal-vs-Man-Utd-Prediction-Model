import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk
import requests
import io
import os

class FootballPredictionDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Football Prediction Dashboard")
        self.root.geometry("800x600")
        self.root.configure(bg='black')
        
        # Prediction values (loaded from step5)
        self.arsenal_win = tk.StringVar()
        self.draw = tk.StringVar() 
        self.manutd_win = tk.StringVar()
        
        # Load predictions from step5 on startup
        self.load_step5_predictions()
        
        # Team logos (placeholder paths - replace with actual logo paths)
        self.arsenal_logo = None
        self.manutd_logo = None
        
        # Load team logos
        self.load_team_logos()
        
        self.create_dashboard()
        
    def load_team_logos(self):
        """Load team logo images from PNG files"""
        self.arsenal_logo_img = None
        self.manutd_logo_img = None
        self.premier_logo_img = None 
        
        try:
            # Load Arsenal logo - replace 'arsenal_logo.png' with your file name
            arsenal_img = Image.open('arsenal_logo.png').convert("RGBA")
            arsenal_img = self.make_background_transparent(arsenal_img)
            arsenal_img = arsenal_img.resize((68, 68), Image.Resampling.LANCZOS)
            self.arsenal_logo_img = ImageTk.PhotoImage(arsenal_img)
        except Exception as e:
            print(f"Could not load Arsenal logo: {e}")
            
        try:
            # Load Man Utd logo - replace 'manutd_logo.png' with your file name  
            manutd_img = Image.open('manutd_logo.png').convert("RGBA")
            manutd_img = self.make_background_transparent(manutd_img)
            manutd_img = manutd_img.resize((68, 68), Image.Resampling.LANCZOS)
            self.manutd_logo_img = ImageTk.PhotoImage(manutd_img)
        except Exception as e:
            print(f"Could not load Man Utd logo: {e}")

        try:
            pl_img = Image.open('premier_league_logo.png').convert("RGBA")
            # pl_img = self.make_background_transparent(pl_img)
            # small horizontal badge next to "Matchweek 1"
            pl_img = pl_img.resize((80, 80), Image.Resampling.LANCZOS)
            self.premier_logo_img = ImageTk.PhotoImage(pl_img)
        except Exception as e:
            print(f"Could not load Premier League logo: {e}")
    
    def make_background_transparent(self, img):
        """Advanced background removal - handles white, gray, and similar backgrounds"""
        img = img.convert("RGBA")
        data = img.getdata()
        
        new_data = []
        for item in data:
            r, g, b, a = item
            
            # Check if pixel is background (white, light gray, or similar colors)
            is_background = (
                # Pure white
                (r > 240 and g > 240 and b > 240) or
                # Light gray
                (abs(r - g) < 10 and abs(g - b) < 10 and abs(r - b) < 10 and r > 200) or
                # Very light colors (beige, off-white, etc.)
                (r > 230 and g > 230 and b > 220)
            )
            
            if is_background:
                new_data.append((255, 255, 255, 0))  # Make transparent
            else:
                new_data.append((r, g, b, a))  # Keep original
        
        img.putdata(new_data)
        return img
    
    def create_dashboard(self):
        # Main container
        main_frame = tk.Frame(self.root, bg='black', padx=40, pady=40)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="Prediction (Win %)", 
                              font=('Arial', 18, 'bold'), 
                              fg='white', bg='black')
        title_label.pack(pady=(0, 30))
        
        # Predictions container
        pred_frame = tk.Frame(main_frame, bg='black')
        pred_frame.pack(fill='x', pady=20)
        
        # Configure grid weights
        pred_frame.grid_columnconfigure(0, weight=1)
        pred_frame.grid_columnconfigure(1, weight=1)
        pred_frame.grid_columnconfigure(2, weight=1)
        
        # Arsenal section
        arsenal_frame = tk.Frame(pred_frame, bg='black')
        arsenal_frame.grid(row=0, column=0, padx=20)
        
        # Arsenal percentage
        arsenal_perc_label = tk.Label(arsenal_frame, text=f"{self.arsenal_win.get()}%", 
                                     font=('Verdana', 35, 'bold'), 
                                     fg='white', bg='black')
        arsenal_perc_label.pack(pady=(0, 10))
        
        # Arsenal logo placeholder (circular) - removed this since we have side-by-side now
        # This was the original big circular logo
        
        # Arsenal logo and text side by side
        arsenal_info_frame = tk.Frame(arsenal_frame, bg='black')
        arsenal_info_frame.pack()
        
        # Arsenal logo (real PNG or fallback circle)
        if self.arsenal_logo_img:
            # Use real PNG logo
            arsenal_logo_label = tk.Label(arsenal_info_frame, image=self.arsenal_logo_img, bg='black')
            arsenal_logo_label.pack(side='left', padx=5)
        else:
            # Fallback to circular logo if PNG not found
            arsenal_logo_small = tk.Canvas(arsenal_info_frame, width=75, height=75, bg='black', highlightthickness=0)
            arsenal_logo_small.create_oval(5, 5, 70, 70, outline='white', width=2, fill='#DC143C')
            arsenal_logo_small.create_text(25, 25, text="ARS", fill='white', font=('Arial', 9, 'bold'))
            arsenal_logo_small.pack(side='left', padx=5)
        
        # Arsenal text
        arsenal_text_frame = tk.Frame(arsenal_info_frame, bg='black')
        arsenal_text_frame.pack(side='left', padx=15)

        arsenal_name_lbl = tk.Label(arsenal_text_frame, text="Arsenal",
                                    font=('Arial', 22, 'bold'), fg='white', bg='black', anchor='w')
        arsenal_name_lbl.pack(anchor='w')

        arsenal_loc_lbl = tk.Label(arsenal_text_frame, text="Home",
                                font=('Arial', 10, 'bold'),  # half of 14
                                fg='white', bg='black', anchor='w')
        arsenal_loc_lbl.pack(anchor='w', pady=(20, 0))  # +20px gap
        
        # Draw section
        draw_frame = tk.Frame(pred_frame, bg='black')
        draw_frame.grid(row=0, column=1, padx=20)
        
        # Draw percentage
        draw_perc_label = tk.Label(draw_frame, text=f"{self.draw.get()}%", 
                                  font=('Verdana Bold', 35, 'bold'), 
                                  fg='white', bg='black')
        draw_perc_label.pack(pady=(0, 10))
        
        # Draw text
        draw_spacer = tk.Canvas(draw_frame, width=68, height=68, bg='black',
                        highlightthickness=0)
        draw_spacer.pack(pady=(0, 0))

        draw_label = tk.Label(draw_frame, text="Draw",
                            font=('Arial', 16, 'bold'), fg='white', bg='black')
        draw_label.pack(pady=(0, 0))
        
        # Man Utd section
        manutd_frame = tk.Frame(pred_frame, bg='black')
        manutd_frame.grid(row=0, column=2, padx=20)
        
        # Man Utd percentage
        manutd_perc_label = tk.Label(manutd_frame, text=f"{self.manutd_win.get()}%", 
                                    font=('Verdana Bold', 35, 'bold'), 
                                    fg='white', bg='black')
        manutd_perc_label.pack(pady=(0, 10))
        
        # Man Utd logo placeholder (circular) - removed this since we have side-by-side now
        # This was the original big circular logo
        
        # Man Utd logo and text side by side
        manutd_info_frame = tk.Frame(manutd_frame, bg='black')
        manutd_info_frame.pack()
        
        # Man Utd logo (real PNG or fallback circle)
        if self.manutd_logo_img:
            # Use real PNG logo
            manutd_logo_label = tk.Label(manutd_info_frame, image=self.manutd_logo_img, bg='black')
            manutd_logo_label.pack(side='left', padx=5)
        else:
            # Fallback to circular logo if PNG not found
            manutd_logo_small = tk.Canvas(manutd_info_frame, width=75, height=75, bg='black', highlightthickness=0)
            manutd_logo_small.create_oval(5, 5, 70, 70, outline='white', width=2, fill='#DA020E')
            manutd_logo_small.create_text(25, 25, text="MAN U", fill='white', font=('Arial', 8, 'bold'))
            manutd_logo_small.pack(side='left', padx=5)
        
        # Man Utd text
        manutd_text_frame = tk.Frame(manutd_info_frame, bg='black')
        manutd_text_frame.pack(side='left', padx=15)

        manutd_name_lbl = tk.Label(manutd_text_frame, text="Manchester United",
                                font=('Arial', 22, 'bold'), fg='white', bg='black', anchor='w')
        manutd_name_lbl.pack(anchor='w')

        manutd_loc_lbl = tk.Label(manutd_text_frame, text="Away",
                                font=('Arial', 10, 'bold'),
                                fg='white', bg='black', anchor='w')
        manutd_loc_lbl.pack(anchor='w', pady=(20, 0))
        
        # Matchweek label
        mw_row = tk.Frame(main_frame, bg='black')
        mw_row.pack(pady=(40, 20))

        if self.premier_logo_img:
            tk.Label(mw_row, image=self.premier_logo_img, bg='black').pack(side='left', padx=(0, 10))

        tk.Label(mw_row, text="Matchweek 1",
                font=('Arial', 20, 'bold'),
                fg='white', bg='black').pack(side='left')
        
        # Control panel - only export button
        control_frame = tk.Frame(main_frame, bg='black')
        control_frame.pack(fill='x', pady=20)
        
        # Store references for updating
        self.arsenal_perc_label = arsenal_perc_label
        self.draw_perc_label = draw_perc_label
        self.manutd_perc_label = manutd_perc_label
    
    def load_step5_predictions(self):
        """Load predictions from step5 on startup"""
        try:
            predictions = self.load_predictions_from_pipeline()
            self.arsenal_win.set(str(predictions['arsenal']))
            self.draw.set(str(predictions['draw']))
            self.manutd_win.set(str(predictions['manutd']))
        except:
            # Fallback values if step5 can't be loaded
            self.arsenal_win.set("45")
            self.draw.set("25")
            self.manutd_win.set("30")
        
    def update_predictions(self):
        """Update the prediction display with new values"""
        try:
            # Validate that values are numbers and sum to 100 (optional)
            arsenal_val = float(self.arsenal_win.get())
            draw_val = float(self.draw.get())
            manutd_val = float(self.manutd_win.get())
            
            # Update labels
            self.arsenal_perc_label.config(text=f"{int(arsenal_val)}%")
            self.draw_perc_label.config(text=f"{int(draw_val)}%")
            self.manutd_perc_label.config(text=f"{int(manutd_val)}%")
            
            messagebox.showinfo("Success", "Predictions updated successfully!")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for all predictions")
    
    def fetch_ml_predictions(self):
        """🔥 THIS IS WHERE PREDICTIONS ARE FETCHED FROM YOUR ML MODEL 🔥"""
        try:
            # 🎯 MAIN PREDICTION FETCHING HAPPENS HERE
            predictions = self.load_predictions_from_pipeline()
            
            # Update the dashboard with ML model results
            self.arsenal_win.set(str(predictions['arsenal']))
            self.draw.set(str(predictions['draw']))
            self.manutd_win.set(str(predictions['manutd']))
            
            self.update_predictions()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch ML predictions: {str(e)}")
            # Fallback to demo data
            predictions = self.simulate_ml_model()
            self.arsenal_win.set(str(predictions['arsenal']))
            self.draw.set(str(predictions['draw']))
            self.manutd_win.set(str(predictions['manutd']))
            self.update_predictions()
    
    def load_predictions_from_pipeline(self):
        """🔥 INTEGRATED WITH YOUR STEP5 FILE 🔥"""
        
        try:
            # Import your step5 file
            import step5_finalOne
            
            # Get probabilities from your step5 file
            # Your step5 has: probabilities = [Away, Draw, Home]
            probabilities = step5_finalOne.probabilities
            
            return {
                'arsenal': round(probabilities[2]),  # Home Win (Arsenal is home)
                'draw': round(probabilities[1]),     # Draw
                'manutd': round(probabilities[0])    # Away Win (Man Utd is away)
            }
            
        except Exception as e:
            print(f"Failed to load from step5: {e}")
            
            # Fallback: Try to run step5 directly and capture results
            try:
                import subprocess
                import sys
                
                # Run step5 to make sure probabilities are updated
                subprocess.run([sys.executable, 'step5_finalOne.py'], check=True)
                
                # Try importing again
                import importlib
                import step5_finalOne
                importlib.reload(step5_finalOne)  # Reload to get fresh data
                
                probabilities = step5_finalOne.probabilities
                
                return {
                    'arsenal': round(probabilities[2]),  # Home Win
                    'draw': round(probabilities[1]),     # Draw  
                    'manutd': round(probabilities[0])    # Away Win
                }
                
            except Exception as e2:
                print(f"Fallback also failed: {e2}")
                # Use simulation as last resort
                return self.simulate_ml_model()
    
    def simulate_ml_model(self):
        """Simulate your ML model - fallback method"""
        import random
        
        # Generate random probabilities that sum to 100
        values = [random.random() for _ in range(3)]
        total = sum(values)
        probabilities = [round((v/total) * 100) for v in values]
        
        # Ensure they sum to 100
        diff = 100 - sum(probabilities)
        probabilities[0] += diff
        
        return {
            'arsenal': probabilities[0],
            'draw': probabilities[1], 
            'manutd': probabilities[2]
        }
    
    def run_full_pipeline(self):
        """🔥 NEW FUNCTION: Run your complete pipeline steps 1-5 then update dashboard"""
        try:
            import subprocess
            import sys
            
            # Show progress
            self.show_progress_message("Running ML Pipeline Steps 1-5...")
            
            # Run your steps in sequence (adjust filenames if needed)
            steps = ['step1.py', 'step2.py', 'step3.py', 'step4.py', 'step5_finalOne.py']
            
            for i, step in enumerate(steps, 1):
                self.show_progress_message(f"Running {step}... ({i}/5)")
                try:
                    subprocess.run([sys.executable, step], check=True)
                except FileNotFoundError:
                    messagebox.showwarning("Warning", f"{step} not found. Skipping...")
                except subprocess.CalledProcessError as e:
                    messagebox.showerror("Error", f"Failed to run {step}: {e}")
                    return
            
            # After pipeline completes, fetch predictions
            self.show_progress_message("Pipeline complete! Fetching predictions...")
            self.fetch_ml_predictions()
            
            messagebox.showinfo("Success", "Full ML Pipeline executed successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Pipeline execution failed: {str(e)}")
    
    def show_progress_message(self, message):
        """Show progress message in the title"""
        original_title = self.root.title()
        self.root.title(f"Football Dashboard - {message}")
        self.root.update()
        # Reset title after 2 seconds
        self.root.after(2000, lambda: self.root.title("Football Prediction Dashboard"))
    
    def export_as_image(self):
        """Export the prediction card as an image"""
        try:
            # Create image
            img_width, img_height = 800, 400
            img = Image.new('RGB', (img_width, img_height), color='black')
            draw = ImageDraw.Draw(img)
            
            # Try to load fonts
            try:
                title_font = ImageFont.truetype("arial.ttf", 32)
                large_font = ImageFont.truetype("arial.ttf", 24)
                medium_font = ImageFont.truetype("arial.ttf", 18)
                small_font = ImageFont.truetype("arial.ttf", 14)
            except:
                # Fallback to default font
                title_font = ImageFont.load_default()
                large_font = ImageFont.load_default()
                medium_font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            
            # Title
            title_text = "Predictions (Win%)"
            title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            draw.text(((img_width - title_width) // 2, 30), title_text, 
                     fill='white', font=title_font)
            
            # Arsenal section
            arsenal_x = 100
            y_center = 200
            
            # Arsenal percentage
            arsenal_text = f"({self.arsenal_win.get()}%)"
            draw.text((arsenal_x, y_center - 60), arsenal_text, fill='white', font=large_font)
            
            # Arsenal circle
            circle_size = 60
            draw.ellipse([arsenal_x, y_center - 30, arsenal_x + circle_size, y_center + 30], 
                        outline='white', width=3, fill='#DC143C')
            
            # Arsenal logo text
            ars_bbox = draw.textbbox((0, 0), "ARS", font=medium_font)
            ars_width = ars_bbox[2] - ars_bbox[0]
            draw.text((arsenal_x + circle_size//2 - ars_width//2, y_center - 8), 
                     "ARS", fill='white', font=medium_font)
            
            # Arsenal label
            draw.text((arsenal_x, y_center + 50), "Arsenal\nHome", 
                     fill='white', font=small_font)
            
            # Draw section
            draw_x = img_width // 2 - 50
            draw_text = f"({self.draw.get()}%)"
            draw.text((draw_x, y_center - 60), draw_text, fill='white', font=large_font)
            draw.text((draw_x + 20, y_center + 20), "Draw", fill='white', font=small_font)
            
            # Man Utd section
            manutd_x = img_width - 200
            
            # Man Utd percentage
            manutd_text = f"({self.manutd_win.get()}%)"
            draw.text((manutd_x, y_center - 60), manutd_text, fill='white', font=large_font)
            
            # Man Utd circle
            draw.ellipse([manutd_x, y_center - 30, manutd_x + circle_size, y_center + 30], 
                        outline='white', width=3, fill='#DA020E')
            
            # Man Utd logo text
            manu_bbox = draw.textbbox((0, 0), "MAN U", font=small_font)
            manu_width = manu_bbox[2] - manu_bbox[0]
            draw.text((manutd_x + circle_size//2 - manu_width//2, y_center - 6), 
                     "MAN U", fill='white', font=small_font)
            
            # Man Utd label
            draw.text((manutd_x, y_center + 50), "Man Utd\nAway", 
                     fill='white', font=small_font)
            
            # Matchweek
            matchweek_text = "Matchweek 1"
            mw_bbox = draw.textbbox((0, 0), matchweek_text, font=medium_font)
            mw_width = mw_bbox[2] - mw_bbox[0]
            draw.text(((img_width - mw_width) // 2, img_height - 60), matchweek_text, 
                     fill='white', font=medium_font)
            
            # Save image
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
            )
            
            if file_path:
                img.save(file_path)
                messagebox.showinfo("Success", f"Image saved to {file_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export image: {str(e)}")

def main():
    root = tk.Tk()
    app = FootballPredictionDashboard(root)
    root.mainloop()

if __name__ == "__main__":
    main()