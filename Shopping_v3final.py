import os
import re 
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
from fpdf import FPDF
import sys
import time
import random

# --- FINAL PDF ENGINE: OPTION 1 (ARCHITECT LOOK) ---
class ShoppingPDF(FPDF):
    def create_shopping_list(self, list_name, user_name, items, total_val, save_path, show_prices):
        while True:
            try:
                self.add_page()
                
                # --- OPTION 1 HEADER: THE ARCHITECT ---
                display_name = (list_name if list_name else "SHOPPING LIST").upper()
                
                # Top Thick Line
                self.set_draw_color(40, 40, 40)
                self.set_line_width(0.8)
                self.line(10, 15, 200, 15)
                
                # Title Text
                self.ln(7)
                self.set_text_color(40, 40, 40)
                self.set_font("Helvetica", style='B', size=18)
                self.cell(0, 10, txt=display_name, ln=True, align='C')
                
                # Bottom Thin Line
                self.set_line_width(0.2)
                self.line(10, self.get_y() + 1, 200, self.get_y() + 1)
                
                # User and Date Info
                self.set_font("Helvetica", size=9)
                self.set_text_color(100, 100, 100)
                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                self.ln(3)
                self.cell(0, 5, txt=f"FOR: {user_name} | DATE: {now}", ln=True, align='C')
                self.ln(8)

                count = len(items)
                if count == 0: return False
                
                # VERIFIED V2.8 LOGIC: Columns trigger at 28 items
                page_height_limit = 260 
                use_columns = True if count > 28 else False
                items_per_col = (count // 2) + (count % 2) if use_columns else count
                
                available_h = page_height_limit - self.get_y() - 20
                calc_lh = available_h / items_per_col
                
                if use_columns:
                    f_size = max(10, min(13, calc_lh * 2.1))
                    line_h = max(5.5, min(9, calc_lh))
                    col_w = 95
                else:
                    f_size = max(10, min(16, calc_lh * 1.8))
                    line_h = max(7, min(14, calc_lh))
                    col_w = 190

                # VERIFIED V2.8 LOGIC: Currency Encoding
                symbol_txt = chr(163).encode('latin-1', 'replace').decode('latin-1')
                symbol_w = self.get_string_width(symbol_txt)
                
                start_y = self.get_y()
                self.set_text_color(40, 40, 40)
                
                for i, (name, price) in enumerate(items):
                    if use_columns and i == items_per_col:
                        self.set_xy(110, start_y)
                    
                    if self.get_y() > 275:
                        self.add_page()
                        start_y = 20
                        self.set_y(start_y)

                    # Tick Box
                    curr_x = self.get_x()
                    curr_y = self.get_y()
                    self.set_draw_color(160, 160, 160)
                    self.set_line_width(0.2)
                    self.rect(curr_x, curr_y + (line_h/4), 3.5, 3.5) 
                    
                    # Item Text
                    self.set_x(curr_x + 6)
                    self.set_font("Helvetica", size=f_size)
                    safe_name = name.encode('latin-1', 'replace').decode('latin-1')
                    item_display = f"> {safe_name}"
                    
                    if show_prices and price > 0:
                        self.cell(col_w - 28, line_h, txt=item_display)
                        self.set_font("Helvetica", style='B', size=f_size)
                        self.cell(symbol_w + 3, line_h, txt=symbol_txt)
                        self.cell(15, line_h, txt=f"{price:.2f}", ln=True, align='R')
                    else:
                        self.cell(col_w - 6, line_h, txt=item_display, ln=True)
                    
                    self.set_x(110 if use_columns and i >= items_per_col else 10)

                # Footer
                if self.get_y() > 250: self.add_page()
                else: self.ln(5)

                self.set_draw_color(200, 200, 200)
                self.line(10, self.get_y(), 200, self.get_y())
                self.ln(2)
                self.set_font("Helvetica", style='B', size=12)
                self.cell(100, 10, txt=f"TOTAL ITEMS: {len(items)}")
                
                if show_prices and total_val > 0:
                    self.set_x(150)
                    total_str = f"TOTAL: {symbol_txt}{total_val:.2f}"
                    self.cell(50, 10, txt=total_str, ln=True, align='R')
                
                self.output(save_path)
                print(f"\n✅ File saved successfully to: {os.path.basename(save_path)}")
                return True

            except PermissionError:
                print(f"\n⚠️  ERROR: File open. Close PDF and press Enter.")
                input("Press Enter to retry...")
                self.pages = {}; self.page = 0 
                continue 
            except Exception as e:
                print(f"PDF Error: {e}")
                return False

# --- UTILITIES (REMAINING CODE VERIFIED UNTOUCHED FROM V2.8) ---
def clear():
    if os.name == 'nt':
        os.system('cls')
        sys.stdout.write('\033[2J\033[3J\033[H')
    else:
        sys.stdout.write('\033[2J\033[3J\033[H')
    sys.stdout.flush()

def delete_last_lines(n=1):
    for _ in range(n):
        sys.stdout.write('\x1b[1A\x1b[2K') 

def goodbye_exit(name, open_path=None):
    clear()
    print("\n" + "="*55)
    print(f"   Goodbye {name}!")
    print("   Thanks for using Ricky's Shopping List Creation Tool")
    print("="*55)
    time.sleep(2.0)
    if open_path:
        try: os.startfile(open_path)
        except: pass
    sys.exit()

def sort_my_list(foods_list, prices_list):
    if not foods_list: return [], []
    combined = list(zip(foods_list, prices_list))
    combined.sort(key=lambda x: re.sub(r'^\d+[Xx]\s+', '', x[0]).upper())
    new_f, new_p = zip(*combined)
    return list(new_f), list(new_p)

def get_valid_price(prompt, default_val=0.0):
    while True:
        p_in = input(prompt).strip()
        if not p_in: return default_val
        try:
            return float(p_in)
        except ValueError:
            print("⚠️ Invalid price! Please enter a number.")
            time.sleep(1.5)
            delete_last_lines(2)

# --- START ---
currency = "£"
clear()
print("--- RICKY'S PDF SHOPPING LIST CREATOR ---")

foods, prices, total = [], [], 0.0
list_name = ""

user_name_in = input("\nWho am I making this list for today? ").strip().capitalize()
user_name = user_name_in if user_name_in else "Valued Customer"

greetings = ["Happy shopping", "Let's get organized", "Hope you find some deals", "Ready when you are"]
print(f"{random.choice(greetings)}, {user_name}!")

price_mode_in = input("\nWould you like to include prices for this list? (y/n): ").lower().strip()
use_prices = True if price_mode_in == 'y' else False

while True:
    print(f"\n[1] Start New List\n[2] Import Existing List (.txt)\n[3] Exit")
    start_choice = input("\nSelect (1-3): ").strip()

    if start_choice == '3': goodbye_exit(user_name)
    elif start_choice == '2':
        root = tk.Tk(); root.withdraw(); root.attributes("-topmost", True)
        import_path = filedialog.askopenfilename(title="Open List", filetypes=[("Text Files", "*.txt")])
        root.destroy()
        if import_path:
            clear()
            try:
                with open(import_path, "r", encoding="utf-8", errors='replace') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("NAME:"):
                            list_name = line.replace("NAME:", "").strip().upper()
                        if line.startswith(">"):
                            match = re.search(r">\s*(.+?)(?:\s+[. ]*\s*£?\s*(\d+\.\d{2}))?$", line)
                            if match:
                                item_name = match.group(1).strip()
                                item_price = float(match.group(2)) if match.group(2) else 0.0
                                foods.append(item_name); prices.append(item_price); total += item_price
                if not list_name: list_name = f"{user_name.upper()}'S IMPORTED LIST"
                foods, prices = sort_my_list(foods, prices)
                clear()
                print(f"✅ Loaded: {list_name}") 
                input("\nPress Enter to start...")
                break
            except: 
                print("Error loading file."); time.sleep(1); clear()
        else:
            print("⚠️ No file selected."); time.sleep(1.2); clear()
    elif start_choice == '1':
        clear()
        store_tag = input("Enter store (e.g. ASDA): ").strip().upper()
        list_name = f"{user_name.upper()}'S {store_tag or 'SHOPPING'} LIST"
        break

shopping_finished = False
while not shopping_finished:
    clear()
    print(f"--- {list_name} ---")
    print("Commands: 'l' (list), 'r' (remove), 'e' (edit), 'n' (rename the list), 'q' (save)")
    
    while True:
        entry_raw = input("\nEnter Item (or command): ").strip()
        cmd = entry_raw.lower()
        if not entry_raw: delete_last_lines(1); continue
        
        if cmd == 'q': 
            shopping_finished = True
            break
        elif cmd == 'n': 
            print(f"\nCurrent name: {list_name}")
            new_title = input("Enter new list name: ").strip().upper()
            if new_title: list_name = new_title; print("✅ List renamed.")
            else: print("⚠️ Name cannot be empty.")
            time.sleep(1.2); break
        elif cmd in ['l', 'list']:
            clear() 
            print(f"--- CURRENT LIST: {list_name} ---")
            if not foods: print("\nYour list is currently empty.")
            else:
                for i, (f, p) in enumerate(zip(foods, prices), 1):
                    p_disp = f"{currency}{p:>7.2f}" if use_prices and p > 0 else ""
                    print(f"{i:>2}. {f:<33} {p_disp}")
                print(f"{'-'*45}")
                if use_prices: print(f"Total Items: {len(foods):<19} Total: {currency}{total:>7.2f}")
                else: print(f"Total Items: {len(foods)}")
            input("\nPress Enter to return to menu..."); break 
        elif cmd in ['r', 'remove']:
            if not foods: print("\n⚠️ List is empty!"); time.sleep(1.5); break
            while True:
                if not foods: break
                clear()
                print("--- REMOVE ITEMS ---")
                for i, f in enumerate(foods, 1): print(f"{i}. {f}")
                idx_in = input("Number to remove (0 to cancel): ").strip()
                if idx_in == '0' or not idx_in: break
                try:
                    idx = int(idx_in) - 1
                    if 0 <= idx < len(foods): total -= prices.pop(idx); foods.pop(idx)
                    else: print("⚠️ Invalid choice!"); time.sleep(1.2)
                except ValueError: print("⚠️ Please enter a number."); time.sleep(1.2)
            break
        elif cmd in ['e', 'edit']:
            if not foods: print("\n⚠️ List is empty!"); time.sleep(1.5); break
            while True:
                if not foods: break
                clear()
                print("--- EDIT ITEM ---")
                for i, f in enumerate(foods, 1): print(f"{i}. {f}")
                idx_in = input("\nNumber to edit (0 to cancel): ").strip()
                if idx_in == '0' or not idx_in: break
                try:
                    idx = int(idx_in) - 1
                    if 0 <= idx < len(foods):
                        old_p, full_n = prices[idx], foods[idx]
                        qty_match = re.search(r'^(\d+)[Xx]\s+(.+)', full_n)
                        c_qty, c_name = (int(qty_match.group(1)), qty_match.group(2)) if qty_match else (1, full_n)
                        n_qty = int(input(f"New qty ({c_qty}): ") or c_qty)
                        n_name = input(f"New name ({c_name}): ").strip().upper() or c_name
                        n_total_p = 0.0
                        if use_prices:
                            unit_p_old = old_p / c_qty if c_qty > 0 else 0.0
                            unit_p = get_valid_price(f"New price for 1 ({unit_p_old:.2f}): ", unit_p_old)
                            n_total_p = unit_p * n_qty
                        else: n_total_p = old_p
                        total = (total - old_p) + n_total_p
                        prices[idx], foods[idx] = n_total_p, (f"{n_qty}X {n_name}" if n_qty > 1 else n_name)
                        foods, prices = sort_my_list(foods, prices); break
                    else: print("⚠️ Invalid choice!"); time.sleep(1.2)
                except ValueError: print("⚠️ Please enter a number."); time.sleep(1.2)
            break
        else:
            # VERIFIED V2.8 LOGIC: Quantity Detection
            new_qty = 1
            processed_name = entry_raw.strip().upper()

            start_m = re.search(r'^(\d+)\s*[Xx]?\s*(.*)', processed_name)
            if start_m and start_m.group(2):
                new_qty = int(start_m.group(1))
                processed_name = start_m.group(2).strip()
            else:
                end_m = re.search(r'(.*?)\s*(\d+)$', processed_name)
                if end_m and end_m.group(1):
                    new_qty = int(end_m.group(2))
                    processed_name = end_m.group(1).strip()

            if processed_name:
                duplicate_idx = -1
                for i, f in enumerate(foods):
                    if processed_name == re.sub(r'^\d+[Xx]\s+', '', f).upper():
                        duplicate_idx = i; break
                
                if duplicate_idx != -1:
                    print(f"\n⚠️ {processed_name} is already in the list.")
                    if input("Combine with existing? (y/n): ").lower().strip() == 'y':
                        old_f = foods[duplicate_idx]
                        old_qty_m = re.search(r'^(\d+)[Xx]\s+', old_f)
                        old_qty = int(old_qty_m.group(1)) if old_qty_m else 1
                        combined_qty = old_qty + new_qty
                        item_total = 0.0
                        if use_prices:
                            unit_p = get_valid_price(f"Price for 1x {processed_name}: ")
                            item_total = unit_p * new_qty
                        prices[duplicate_idx] += item_total
                        total += item_total
                        foods[duplicate_idx] = f"{combined_qty}X {processed_name}"
                        print(f" >> Updated {processed_name} to {combined_qty}X"); time.sleep(1)
                else:
                    item_total = 0.0
                    if use_prices:
                        unit_p = get_valid_price(f"Price for 1x {processed_name}: ")
                        item_total = unit_p * new_qty
                    disp = f"{new_qty}X {processed_name}" if new_qty > 1 else processed_name
                    foods.append(disp); prices.append(item_total); total += item_total
                    foods, prices = sort_my_list(foods, prices)
                    delete_last_lines(2 if use_prices and item_total > 0 else 1)
                    print(f" >> Added: {disp}")

if foods:
    clear()
    print(f"--- FINAL REVIEW ---")
    for f, p in zip(foods, prices):
        p_disp = f"{currency}{p:>7.2f}" if use_prices and p > 0 else "---"
        print(f"{f:<33} {p_disp}")
    
    if input("\nSave and finish? (y/n): ").lower().strip() == 'y':
        root = tk.Tk(); root.withdraw(); root.attributes("-topmost", True)
        f_path = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=f"{list_name}.pdf")
        root.destroy()
        if f_path:
            pdf = ShoppingPDF()
            if pdf.create_shopping_list(list_name, user_name, list(zip(foods, prices)), total, f_path, use_prices):
                time.sleep(0.5) 
                txt_path = os.path.splitext(f_path)[0] + ".txt"
                with open(txt_path, "w", encoding="utf-8", errors='replace') as tf:
                    tf.write(f"NAME: {list_name}\n")
                    for f, p in zip(foods, prices): tf.write(f"> {f} ... £ {p:.2f}\n")
                if input("\nPrint? (y/n): ").lower().strip() == 'y':
                    try: 
                        os.startfile(f_path, "print")
                        print("🖨️ Sending to printer..."); time.sleep(1) 
                    except: print("⚠️ Printer not found.")
                target_path = f_path if input("\nOpen file now? (y/n): ").lower().strip() == 'y' else None
                goodbye_exit(user_name, target_path)
        goodbye_exit(user_name)
    else: goodbye_exit(user_name)
else: goodbye_exit(user_name)