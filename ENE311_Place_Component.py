## ============================================================================
##  File        : Place_Component.py
##  Description : Utility script for KiCad – Placement & Annotation Helpers
##                For ENE311 : Fundamentals of Electronic Product Design 
##                / PCB Design Class
##
##  Author      : Kittiphop Phanthachart
##  University  : King Mongkut’s University of Technology Thonburi (KMUTT)
##  Faculty     : Engineering
##  Department  : Electronic and Telecommunication Engineering (ENE)
##
##  Created     : 2025-08-19
## ============================================================================

import re
import pcbnew

def _pt(x, y):
    if hasattr(pcbnew, "VECTOR2I"):
        return pcbnew.VECTOR2I(int(x), int(y))
    return pcbnew.wxPoint(int(x), int(y))

def _board():
    b = pcbnew.GetBoard()
    if b is None:
        raise RuntimeError("No board open. Open a PCB in pcbnew first.")
    return b

def _footprints(board=None):
    board = board or _board()
    if hasattr(board, "GetFootprints"):
        return list(board.GetFootprints())
    return list(board.GetModules())

def _zones(board=None):
    board = board or _board()
    if hasattr(board, "Zones"):
        return list(board.Zones())
    zs = []
    if hasattr(board, "GetAreaCount") and hasattr(board, "GetArea"):
        for i in range(board.GetAreaCount()):
            zs.append(board.GetArea(i))
    return zs

def _track_netname(t):
    if hasattr(t, "GetNet") and t.GetNet():
        if hasattr(t.GetNet(), "GetNetname"):
            return t.GetNet().GetNetname()
    if hasattr(t, "GetNetname"):
        return t.GetNetname()
    return None

def mm_to_nm(v: float) -> int:
    return int(round(v * 1_000_000))

def nm_to_mm(v: int) -> float:
    return v / 1_000_000.0

def get_all_component_names():
    board = _board()
    return [fp.GetReference() for fp in _footprints(board)]

def get_wildcard_component_names(pattern: str, all_names=None):
    if all_names is None:
        all_names = get_all_component_names()
    esc = re.escape(pattern).replace(r"\*", ".*").replace(r"\?", ".")
    exp = re.compile(f"^{esc}$")
    return [n for n in all_names if exp.match(n)]

def get_component(name: str):
    board = _board()
    matches = [fp for fp in _footprints(board) if fp.GetReference() == name]
    if not matches:
        raise ValueError(f"Component '{name}' not found.")
    return matches[0]

def place_component_relative_mm(reference_component_name: str,
                                component_to_move: str,
                                rel_x_mm: float, rel_y_mm: float,
                                suppress_refresh: bool = False):
    board = _board()
    a = get_component(reference_component_name)
    b = get_component(component_to_move)
    pos_a = a.GetPosition()
    b.SetPosition(_pt(pos_a.x + mm_to_nm(rel_x_mm), pos_a.y + mm_to_nm(rel_y_mm)))
    if not suppress_refresh:
        pcbnew.Refresh()

def place_components_relative_mm(components_list,
                                 rel_x_mm: float, rel_y_mm: float,
                                 suppress_refresh: bool = False):
    if len(components_list) < 2:
        return
    for i in range(len(components_list) - 1):
        place_component_relative_mm(components_list[i], components_list[i+1],
                                    rel_x_mm, rel_y_mm, True)
    if not suppress_refresh:
        pcbnew.Refresh()

def _justify_from_str(justification: str):
    j = justification.lower()
    if j == "left":
        return pcbnew.GR_TEXT_HJUSTIFY_LEFT
    if j == "right":
        return pcbnew.GR_TEXT_HJUSTIFY_RIGHT
    if j == "center":
        return pcbnew.GR_TEXT_HJUSTIFY_CENTER
    return None

def place_component_reference_position(component_name, rel_x_mm: float, rel_y_mm: float,
                                       justification=None, suppress_refresh: bool = False):
    if isinstance(component_name, (list, tuple)):
        for c in component_name:
            place_component_reference_position(c, rel_x_mm, rel_y_mm, justification, True)
        if not suppress_refresh:
            pcbnew.Refresh()
        return
    a = get_component(component_name)
    ref = a.Reference()
    pos_a = a.GetPosition()
    ref.SetPosition(_pt(pos_a.x + mm_to_nm(rel_x_mm), pos_a.y + mm_to_nm(rel_y_mm)))
    if justification is not None:
        jv = _justify_from_str(justification)
        if jv is not None:
            ref.SetHorizJustify(jv)
    if not suppress_refresh:
        pcbnew.Refresh()

def place_component_value_position(component_name: str, rel_x_mm: float, rel_y_mm: float,
                                   justification=None):
    a = get_component(component_name)
    val = a.Value()
    pos_a = a.GetPosition()
    val.SetPosition(_pt(pos_a.x + mm_to_nm(rel_x_mm), pos_a.y + mm_to_nm(rel_y_mm)))
    if justification is not None:
        jv = _justify_from_str(justification)
        if jv is not None:
            val.SetHorizJustify(jv)
    pcbnew.Refresh()

def place_component_value_to_silk_layer(component_name: str):
    c = get_component(component_name)
    on_back = (c.GetLayer() == pcbnew.B_Cu)
    target_layer = pcbnew.B_SilkS if on_back else pcbnew.F_SilkS
    val = c.Value()
    val.SetLayer(target_layer)
    if hasattr(val, "SetMirrored"):
        val.SetMirrored(on_back)
    pcbnew.Refresh()

def lock_tracks_with_signal_name(signal_names_list, min_width_mm: float = 0.0):
    board = _board()
    min_w = mm_to_nm(min_width_mm)
    to_lock = []
    for t in board.GetTracks():
        wn = _track_netname(t)
        if wn in signal_names_list and t.GetWidth() >= min_w:
            to_lock.append(t)
    for t in to_lock:
        t.SetLocked(True)
    pcbnew.Refresh()

def unlock_tracks_with_signal_name(signal_names_list, min_width_mm: float = 0.0):
    board = _board()
    min_w = mm_to_nm(min_width_mm)
    to_unlock = []
    for t in board.GetTracks():
        wn = _track_netname(t)
        if wn in signal_names_list and t.GetWidth() >= min_w:
            to_unlock.append(t)
    for t in to_unlock:
        t.SetLocked(False)
    pcbnew.Refresh()

def lock_all_tracks(min_width_mm: float = 0.0):
    board = _board()
    min_w = mm_to_nm(min_width_mm)
    for t in board.GetTracks():
        if t.GetWidth() >= min_w:
            t.SetLocked(True)
    pcbnew.Refresh()

def select_all_areas():
    for z in _zones():
        if hasattr(z, "SetSelected"):
            z.SetSelected()
    pcbnew.Refresh()

def create_text_element(text: str, justification=None):
    board = _board()
    te = pcbnew.TEXTE_PCB(board)
    te.SetVisible(True)
    te.SetThickness(mm_to_nm(0.1524))
    te.SetText(text)
    if justification is not None:
        jv = _justify_from_str(justification)
        if jv is not None:
            te.SetHorizJustify(jv)
    return te

def bom_value_legend(x_mm: float, y_mm: float, footprints_to_ignore=None, bottom_silk=False):
    board = _board()
    footprints_to_ignore = footprints_to_ignore or []
    all_names = get_all_component_names()
    ignore_expanded = []
    for patt in footprints_to_ignore:
        ignore_expanded.extend(get_wildcard_component_names(patt, all_names))
    ignore_set = set(ignore_expanded)
    names_left = [n for n in all_names if n not in ignore_set]
    names_left.sort()
    for f in sorted(ignore_set):
        print(f"Ignoring: {f}")
    names_txt = []
    values_txt = []
    column_width = 0
    row_height = 0
    target_layer = pcbnew.B_SilkS if bottom_silk else pcbnew.F_SilkS
    for refname in names_left:
        te_name = create_text_element(refname, "right")
        te_name.SetLayer(target_layer)
        if hasattr(te_name, "SetMirrored"):
            te_name.SetMirrored(bottom_silk)
        names_txt.append(te_name)
        bb = te_name.GetBoundingBox()
        column_width = max(column_width, bb.GetWidth())
        row_height = max(row_height, bb.GetHeight())
        value_str = get_component(refname).Value().GetText()
        te_val = create_text_element(value_str, "left")
        te_val.SetLayer(target_layer)
        if hasattr(te_val, "SetMirrored"):
            te_val.SetMirrored(bottom_silk)
        values_txt.append(te_val)
        bbv = te_val.GetBoundingBox()
        column_width = max(column_width, bbv.GetWidth())
        row_height = max(row_height, bbv.GetHeight())
    offset = mm_to_nm(1.0)
    x0 = mm_to_nm(x_mm)
    y0 = mm_to_nm(y_mm)
    for i in range(len(names_txt)):
        names_txt[i].SetPosition(_pt(x0, y0 + i * row_height))
        values_txt[i].SetPosition(_pt(x0 + (-offset if bottom_silk else offset), y0 + i * row_height))
        board.Add(names_txt[i])
        board.Add(values_txt[i])
    pcbnew.Refresh()

def place_chain_relative(pattern: str, rel_x_mm: float, rel_y_mm: float):
    names = get_wildcard_component_names(pattern)
    if len(names) < 2:
        print("Not enough components match the pattern to place a chain.")
        return
    place_components_relative_mm(names, rel_x_mm, rel_y_mm)

print("Loaded PlaceComponents_py3 utilities. Examples:")
print(" - place_component_relative_mm('U1', 'R1', 0, 2)")
print(" - place_component_reference_position('R1', 0, -1, 'left')")
print(" - place_component_value_to_silk_layer('R1')")
print(" - lock_tracks_with_signal_name(['GND', 'VCC'], min_width_mm=0.25)")
print(" - bom_value_legend(10, 10, ['JP*','TP*'], bottom_silk=False)")
