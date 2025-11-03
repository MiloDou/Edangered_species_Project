import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import numpy as np

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


class TransitionMatrixApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🌿 Especies en Peligro  🌿")
        self.state("zoomed")  
        self.configure(fg_color="#1e2e1f")  


        header = ctk.CTkFrame(self, fg_color="#253b26", corner_radius=12)
        header.pack(fill="x", padx=20, pady=10, ipady=10)

        title = ctk.CTkLabel(
            header,
            text="🌳 Matriz de Transición de Especies — 4x4 🌳",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#e0f5e9"
        )
        title.grid(row=0, column=0, padx=15, pady=5, sticky="w")


        self.species_var = ctk.StringVar(value="Jaguar")
        species_label = ctk.CTkLabel(header, text="Especie:", text_color="#d6ecd8")
        species_label.grid(row=0, column=1, padx=8)
        self.species_combo = ctk.CTkOptionMenu(
            header,
            values=["Jaguar", "Quetzal", "Mono Araña", "Tortuga Marina", "Guacamaya"],
            variable=self.species_var,
            fg_color="#335e3b",
            button_color="#406b48",
            text_color="white"
        )
        self.species_combo.grid(row=0, column=2, padx=8)


        matrix_frame = ctk.CTkFrame(self, fg_color="#203520", corner_radius=15)
        matrix_frame.pack(padx=25, pady=15, fill="x")

        info = ctk.CTkLabel(
            matrix_frame,
            text="Defina la matriz de transición 4x4 (última fila fija: [0,0,0,1]). Cada fila debe sumar 1.",
            wraplength=800,
            text_color="#cfe8d1",
            font=ctk.CTkFont(size=14)
        )
        info.grid(row=0, column=0, columnspan=8, pady=(10, 15))

        self.state_labels = ["No presenta peligro", "Amenazado", "Crítico", "Extinto"]


        for j, label in enumerate(self.state_labels):
            lbl = ctk.CTkLabel(matrix_frame, text=label, text_color="#b0d9b2", font=ctk.CTkFont(size=13, weight="bold"))
            lbl.grid(row=1, column=j + 1, padx=6, pady=6)

        self.matrix_entries = []
        for i in range(4):
            row_entries = []
            rlab = ctk.CTkLabel(matrix_frame, text=f"Desde {self.state_labels[i]}", text_color="#a9d2ad")
            rlab.grid(row=2 + i, column=0, padx=6, pady=6)
            for j in range(4):
                e = ctk.CTkEntry(matrix_frame, width=100, fg_color="#2e4b2f", border_color="#517a55")
                e.grid(row=2 + i, column=1 + j, padx=6, pady=6)
                row_entries.append(e)
            self.matrix_entries.append(row_entries)

        self._set_last_row_fixed()


        btn_frame = ctk.CTkFrame(self, fg_color="#253b26", corner_radius=12)
        btn_frame.pack(padx=20, pady=10, fill="x")

        validate_btn = ctk.CTkButton(btn_frame, text="✅ Validar Matriz", command=self.validate_matrix, fg_color="#4e8a54", hover_color="#5fa762")
        validate_btn.grid(row=0, column=0, padx=10, pady=8)

        preset_btn = ctk.CTkButton(btn_frame, text="🌿 Cargar Ejemplo", command=self.load_example, fg_color="#355f3b", hover_color="#487f4f")
        preset_btn.grid(row=0, column=1, padx=10)

        calc_frame = ctk.CTkFrame(self, fg_color="#203520", corner_radius=15)
        calc_frame.pack(padx=25, pady=10, fill="x")

        self.start_state_var = ctk.StringVar(value=self.state_labels[0])
        self.target_state_var = ctk.StringVar(value=self.state_labels[3])
        self.steps_var = tk.IntVar(value=1)

        start_label = ctk.CTkLabel(calc_frame, text="Estado inicial:", text_color="#d9eedc")
        start_label.grid(row=0, column=0, padx=6, pady=10)
        start_menu = ctk.CTkOptionMenu(calc_frame, values=self.state_labels, variable=self.start_state_var)
        start_menu.grid(row=0, column=1, padx=6)

        target_label = ctk.CTkLabel(calc_frame, text="Estado objetivo:", text_color="#d9eedc")
        target_label.grid(row=0, column=2, padx=6)
        target_menu = ctk.CTkOptionMenu(calc_frame, values=self.state_labels, variable=self.target_state_var)
        target_menu.grid(row=0, column=3, padx=6)

        steps_label = ctk.CTkLabel(calc_frame, text="Pasos n:", text_color="#d9eedc")
        steps_label.grid(row=0, column=4, padx=6)
        steps_spin = ctk.CTkEntry(calc_frame, textvariable=self.steps_var, width=70, fg_color="#2f4a31", border_color="#517a55")
        steps_spin.grid(row=0, column=5, padx=6)

        calc_btn = ctk.CTkButton(calc_frame, text="🔢 Calcular P(n)", command=self.calculate_probability, fg_color="#4a874d", hover_color="#5fa162")
        calc_btn.grid(row=0, column=6, padx=12)

        self.result_label = ctk.CTkLabel(self, text="Resultado: ", text_color="#bce6be", font=ctk.CTkFont(size=14, weight="bold"))
        self.result_label.pack(padx=20, pady=8, anchor="w")


        footer = ctk.CTkLabel(
            self,
            text="🌱 Visual inspirado en la selva tropical de Mesoamérica. 🌱",
            text_color="#96c9a0",
            font=ctk.CTkFont(size=13)
        )
        footer.pack(side="bottom", pady=10)




#Esto como tal es el funcionamiento algo simulado
    def _set_last_row_fixed(self):
        vals = ["0", "0", "0", "1"]
        last = self.matrix_entries[3]
        for j, e in enumerate(last):
            e.delete(0, tk.END)
            e.insert(0, vals[j])
            e.configure(state="disabled")

    def load_example(self):
        ex = np.array([
            [0.7, 0.2, 0.05, 0.05],
            [0.1, 0.6, 0.2, 0.1],
            [0.05, 0.25, 0.6, 0.1],
            [0.0, 0.0, 0.0, 1.0]
        ])
        for i in range(4):
            for j in range(4):
                e = self.matrix_entries[i][j]
                if e.cget("state") != "disabled":
                    e.delete(0, tk.END)
                    e.insert(0, str(float(ex[i, j])))

    def get_matrix(self):
        M = np.zeros((4, 4), dtype=float)
        for i in range(4):
            for j in range(4):
                e = self.matrix_entries[i][j]
                txt = e.get().strip()
                try:
                    val = float(txt)
                except ValueError:
                    raise ValueError(f"Entrada inválida en fila {i+1}, columna {j+1}: '{txt}'")
                M[i, j] = val
        return M

    def validate_matrix(self):
        try:
            M = self.get_matrix()
        except ValueError as ex:
            messagebox.showerror("Error", str(ex))
            return False

        if not np.allclose(M[3], np.array([0, 0, 0, 1]), atol=1e-9):
            messagebox.showerror("Error", "La última fila debe ser [0, 0, 0, 1].")
            return False

        for i in range(4):
            s = M[i].sum()
            if not np.isclose(s, 1.0, atol=1e-6):
                messagebox.showerror("Error", f"La fila {i+1} no suma 1 (suma = {s}).")
                return False

        messagebox.showinfo("OK", "Matriz válida ✅")
        return True

    def calculate_probability(self):
        if not self.validate_matrix():
            return
        try:
            M = self.get_matrix()
            n = int(self.steps_var.get())
            if n < 0:
                raise ValueError()
        except Exception:
            messagebox.showerror("Error", "Número de pasos inválido (entero >= 0).")
            return

        start_idx = self.state_labels.index(self.start_state_var.get())
        target_idx = self.state_labels.index(self.target_state_var.get())

        Mn = np.linalg.matrix_power(M, n)
        prob = Mn[start_idx, target_idx]
        self.result_label.configure(text=f"Resultado: P({self.start_state_var.get()} → {self.target_state_var.get()}, n={n}) = {prob:.6f}")


if __name__ == "__main__":
    app = TransitionMatrixApp()
    app.mainloop()
