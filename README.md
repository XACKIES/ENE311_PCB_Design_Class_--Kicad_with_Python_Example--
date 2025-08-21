# ENE311_PCB_Design_Class_"Kicad_with_Python_Example"
created by [Kittiphop Phanthachart](https://bento.me/mac-kittiphop) (a 4th-year Engineering student)


[PCB_Design_Manual Doc](https://docs.google.com/document/d/1T2QgssXLalr-_P1kaVpM2Z5Q4rbRVg9ENvGY7iWf7Jk/edit?usp=sharing)
---


Main Drive : [PCB Design Reference](https://drive.google.com/drive/folders/1iH3Fwa9-kuD3eO-nP3mI9ks_AyRZPl0m?usp=drive_link)


Slide presentation file : [ENE311_PCB_Design_Slide.pdf](https://drive.google.com/file/d/1ZLuTyXhizw9S3qezdIU1Z15aCVTSmlFd/view?usp=drive_link)



---


# Place_Component.py

Utilities for **KiCad pcbnew (Python 3)** — quick placement, text annotation, track locking, and a silkscreen BOM legend.  
Tested with **KiCad ** .

> For ENE311: Fundamentals of Electronic Product Design / PCB Design Class  
> King Mongkut’s University of Technology Thonburi (KMUTT), ENE

---

## ✨ Features
- Place one component **relative** to another (mm offsets)
- Place a **chain** of components horizontally/vertically
- Adjust **Reference**/**Value** text position & justification
- Move **Value** text to the correct **silkscreen** (auto-mirror on back)
- **Lock/Unlock** tracks by net name (with min width filter)
- Quick **BOM legend** on silkscreen: `Reference | Value`
- Wildcard selection (e.g., `R*`, `C10?`, `U?3`)

---

## 📦 Requirements
- KiCad **Pcbnew** (v6/v7/v8)
- Python 3 environment bundled with KiCad  
  (open via **Tools → Scripting Console** inside Pcbnew)

---

## 🚀 Quick Start

1. Open your PCB in **Pcbnew**  
2. Open **Tools → Scripting Console**  
3. Load the script (adjust the path):

   ```python
   exec(open(r"C:\Github_Project\ENE311_PCB_Design_Class_--Kicad_with_Python_Example--\ENE311_Place_Component.py").read())
   ```

You should see:
```
Loaded PlaceComponents_py3 utilities. Examples:
 - place_component_relative_mm('U1', 'R1', 0, 2)
 ...
```

---

## 🧪 Examples

### Place components in a row (horizontal)
```python
place_components_relative_mm(["R1","R2","R3","R4"], 2, 0)
# R2..R4 placed to the right of the previous part, 2 mm spacing
```

### Place components in a column (vertical)
```python
place_components_relative_mm(["C1","C2","C3"], 0, 1.5)
# C2 and C3 placed below the previous part, 1.5 mm spacing
```

### Place one component relative to another
```python
place_component_relative_mm("U1", "R1", 3, 1)
# Move R1 to be 3 mm right and 1 mm below U1
```

### Adjust reference text (REF**)
```python
place_component_reference_position("R1", 0, 1, "center")
# Move R1’s reference text 1 mm above, centered
```

### Adjust value text (VALUE)
```python
place_component_value_position("R1", 0, -1, "center")
# Move R1’s value text 1 mm below, centered
```

### Put value text on silkscreen (auto front/back + mirror)
```python
place_component_value_to_silk_layer("R1")
```

### Lock / Unlock tracks by net name
```python
lock_tracks_with_signal_name(["GND","VCC"], min_width_mm=0.25)
unlock_tracks_with_signal_name(["GND"])
```

### Create a BOM legend on silkscreen
```python
bom_value_legend(10, 10, ["JP*","TP*"], bottom_silk=False)
# Front silkscreen at (10 mm, 10 mm); ignores JP* and TP*
```

### Wildcard helpers
```python
get_all_component_names()               # List all component references
get_wildcard_component_names("R*")      # e.g., R1, R2, ...
get_wildcard_component_names("C1?")     # e.g., C10..C19
```

---

## 🧩 One-shot Demo Snippet

Copy–paste to perform a mini layout exercise:

```python
# 1) Horizontal resistor row (2.0 mm spacing)
place_components_relative_mm(["R1","R2","R3","R4","R5"], 2.0, 0.0)

# 2) Reference above, centered
place_component_reference_position(["R1","R2","R3","R4","R5"], 0.0, 1.0, "center")

# 3) Value below, centered, on silks
for r in ["R1","R2","R3","R4","R5"]:
    place_component_value_position(r, 0.0, -1.0, "center")
    place_component_value_to_silk_layer(r)

# 4) Lock main power rails (>= 0.25 mm)
lock_tracks_with_signal_name(["GND","VCC"], min_width_mm=0.25)

# 5) Compact BOM legend on F.Silk at (15, 10) mm
bom_value_legend(15, 10, ["JP*","TP*"], bottom_silk=False)
```

---

## 🛠️ Notes & Tips
- **Units:** offsets are in **mm**; internally converted to **nm**
- If nothing moves, check that references (e.g., `"R1"`) **exist** on the board
- Force a redraw any time with:
  ```python
  pcbnew.Refresh()
  ```
- Back-side footprints: value text is **mirrored automatically** for readability

