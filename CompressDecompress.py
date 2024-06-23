import tkinter as tk
from tkinter import filedialog, messagebox
import zstandard as zstd
import struct


# Function to select files
def select_files():
    files = filedialog.askopenfilenames(title='Select Files')
    if files:
        file_list.delete(0, tk.END)
        for file in files:
            filename = file.split('/')[-1]
            file_list.insert(tk.END, filename)
        file_list.filepaths = files


# Function to compress files
def compress_files():
    disable_buttons()
    working_label.config(text='Compressing...')
    working_label.pack(pady=10)

    if not hasattr(file_list, 'filepaths'):
        messagebox.showwarning('No Files', 'Please select files to compress.')
        working_label.forget()
        enable_buttons()
        return

    output_file = filedialog.asksaveasfilename(defaultextension='.zst',
                                               filetypes=[('Zstandard files', '*.zst')],
                                               title='Save As',
                                               initialfile='*.zst')
    if not output_file:
        working_label.forget()
        enable_buttons()
        return

    compressor = zstd.ZstdCompressor(level=22)
    try:
        with open(output_file, 'wb') as f_out:
            for file in file_list.filepaths:
                try:
                    with open(file, 'rb') as f_in:
                        file_content = f_in.read()
                    compressed_content = compressor.compress(file_content)
                    filename = file.split('/')[-1]
                    f_out.write(struct.pack('I', len(filename)))
                    f_out.write(filename.encode())
                    f_out.write(struct.pack('I', len(compressed_content)))
                    f_out.write(compressed_content)
                    file_list.delete(0, tk.END)
                except Exception as e:
                    messagebox.showerror('Error', 'Failed to decompress file ' + file + ': ' + str(e))
                    return
        messagebox.showinfo('Success', 'Files compressed to ' + output_file)
    except Exception as e:
        messagebox.showerror('Error', 'Failed to write compressed file: ' + str(e))
    finally:
        working_label.forget()
        enable_buttons()


# Function to decompress files
def decompress_files():
    disable_buttons()
    working_label.config(text='Decompressing...')
    working_label.pack(pady=10)

    if not hasattr(file_list, 'filepaths'):
        messagebox.showwarning('No Files', 'Please select files to decompress.')
        working_label.forget()
        enable_buttons()
        return

    zst_files_selected = all(file.endswith('.zst') for file in file_list.filepaths)
    if not zst_files_selected:
        messagebox.showwarning('.zst Files Error', 'Please only select .zst files to decompress.')
        working_label.forget()
        enable_buttons()
        return

    output_dir = filedialog.askdirectory(title='Select Output Directory')
    if not output_dir:
        working_label.forget()
        enable_buttons()
        return

    decompressor = zstd.ZstdDecompressor()
    for file in file_list.filepaths:
        try:
            with open(file, 'rb') as f_in:
                while True:
                    filename_size_data = f_in.read(4)
                    if not filename_size_data:
                        break
                    filename_size = struct.unpack('I', filename_size_data)[0]
                    filename = f_in.read(filename_size).decode()
                    compressed_size = struct.unpack('I', f_in.read(4))[0]
                    compressed_content = f_in.read(compressed_size)
                    decompressed_content = decompressor.decompress(compressed_content)
                    output_file_path = output_dir + '/' + filename
                    with open(output_file_path, 'wb') as f_out:
                        f_out.write(decompressed_content)
                    file_list.delete(0, tk.END)
            messagebox.showinfo('Success', 'File ' + file + ' decompressed to ' + output_dir)
        except Exception as e:
            messagebox.showerror('Error', 'Failed to decompress file ' + file + ': ' + str(e))
        finally:
            working_label.forget()
            enable_buttons()


# Function to disable GUI buttons
def disable_buttons():
    browse_button.config(state='disabled')
    compress_button.config(state='disabled')
    decompress_button.config(state='disabled')


# Function to enable GUI buttons
def enable_buttons():
    browse_button.config(state='normal')
    compress_button.config(state='normal')
    decompress_button.config(state='normal')


# Main GUI Code
root = tk.Tk()
root.title('Compression/Decompression Program')

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)
file_list_label = tk.Label(frame, text='Files to Process:', font=('Arial', 13, 'bold'))
file_list_label.pack(side=tk.TOP, padx=10, pady=5)
file_list = tk.Listbox(frame, selectmode=tk.MULTIPLE, width=50, height=10, font=('Arial', 12))
file_list.pack(side=tk.TOP, padx=10, pady=(0, 10))
button_frame = tk.Frame(frame)
button_frame.pack(side=tk.TOP, padx=10, pady=(0, 10))
browse_button = tk.Button(button_frame, text="Browse Files", command=select_files, width=15, font=('Arial', 13))
browse_button.pack(pady=10)
compress_button = tk.Button(button_frame, text="Compress", command=compress_files, width=13, font=('Arial', 12))
compress_button.pack(side=tk.LEFT, padx=10, pady=10)
decompress_button = tk.Button(button_frame, text="Decompress", command=decompress_files, width=13, font=('Arial', 12))
decompress_button.pack(side=tk.RIGHT, padx=10, pady=10)
working_label = tk.Label(frame, text='', font=('Arial', 15, 'bold'))

root.mainloop()
