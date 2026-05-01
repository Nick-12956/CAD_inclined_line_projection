from pyautocad import Autocad, APoint
import re
import math

acad = Autocad(create_if_not_exists=True)

def initial_settings():
    doc = acad.app.ActiveDocument
    doc.SendCommand('-UNITS 2 0 1 0 0 N ')
    doc.SendCommand('DIMTXT 2.5 ')
    doc.SendCommand('DIMASZ 2.5 ')
    doc.SendCommand('DIMDEC 0 ') 
    doc.SendCommand('LWDISPLAY ON ')

def extract_parameters(question: str) -> dict:
    q = question.lower()

    is_hp = "parallel to hp" in q or "parallel to the hp" in q
    is_vp = "parallel to vp" in q or "parallel to the vp" in q

    match = re.search(r'(\d+)\s*mm\s+above\s+hp', q)
    above = float(match.group(1)) if match else 0.0

    match = re.search(r'(\d+)\s*mm\s+infront\s+of\s+vp', q)
    front = float(match.group(1)) if match else 0.0

    match = re.search(r'(\d+)\s*°', q)
    angle = float(match.group(1)) if match else 0.0

    match = re.search(r'length\s*(\d+)\s*mm', q)
    length = float(match.group(1)) if match else 0.0

    match = re.search(r'line\s+([a-z])([a-z])', q)
    match1 = re.search(r'end\s+([a-z])', q)
    p1 = match1.group(1)
    p2 = 'a'
    if p1 == match.group(1):
        p2 = match.group(2)
    else:
        p2 = match.group(1)
    return {
        "p1": p1, "p2": p2, "length": length, "angle": angle,
        "is_hp": is_hp, "is_vp": is_vp,
        "above": above, "front": front
    }

def draw_projection():
    initial_settings()
    print("<--- Open Complete --->")
    question = input("Enter Problem Statement: ")
    p = extract_parameters(question)

    # 1. Labels and XY Line
    draw_line(APoint(-100.0, 0.0), APoint(200.0, 0.0), color=7, lw=-1)
    acad.model.AddText("X", APoint(-105.0, 2.0), 4)
    acad.model.AddText("Y", APoint(205.0, 2.0), 4)
    acad.model.AddText("F.V.", APoint(-75.0, 15), 4)
    acad.model.AddText("T.V.", APoint(-75.0, -15), 4)
    
    d1=0.0;d2=0.0;d3=0.0;d4=0.0
    if p['is_vp']:
        d1=APoint(0.0, p['above'])
        d2=APoint(p['length'] * math.cos(math.radians(p['angle'])), p['above'] + p['length'] * math.sin(math.radians(p['angle'])))
        d3=APoint(0.0,-p['front'])
        d4=APoint(p['length'] * math.cos(math.radians(p['angle'])),-p['front'])
        draw_line(d1, d2, color=7, lw=30)
        draw_line(d3, d4, color=7, lw=30)
        draw_line(d1, APoint(30.0, p['above']), color=7, lw=-1)
        acad.model.AddText(p['p1']+"'", APoint(d1.x, d1.y + 5), 3)
        acad.model.AddText(p['p2']+"'", APoint(d2.x, d2.y + 5), 3)
        acad.model.AddText(p['p1'], APoint(d3.x, d3.y - 5), 3)
        acad.model.AddText(p['p2'], APoint(d4.x, d4.y - 5), 3)
        acad.model.AddDimRotated(APoint(0.0, 0.0), d1, APoint(-10, p['above']/2), 1.5708)
        acad.model.AddDimAligned(d1, d2, APoint(d1.x, d1.y + 15))
        acad.model.AddDimAngular(d1, d2, APoint(30.0, p['above']),APoint(d1.x + 20, d1.y + 5))
        if float(p.get('front', 0)) != 0.0:
            acad.model.AddDimRotated(APoint(0.0, 0.0), d3, APoint(-10, -p['front']/2), 1.5708)
    else:
        d1=APoint(0.0, -p['front'])
        d2=APoint(p['length'] * math.cos(math.radians(p['angle'])), -(p['front'] + p['length'] * math.sin(math.radians(p['angle']))))
        d3=APoint(0.0, p['above'])
        d4=APoint(p['length'] * math.cos(math.radians(p['angle'])),p['above'])
        draw_line(d1, d2, color=7, lw=30)
        draw_line(d3, d4, color=7, lw=30)
        draw_line(d1, APoint(30.0, -p['front']), color=7, lw=-1)
        acad.model.AddText(p['p1'], APoint(d1.x, d1.y - 5), 3)
        acad.model.AddText(p['p2'], APoint(d2.x, d2.y - 5), 3)
        acad.model.AddText(p['p1']+"'", APoint(d3.x, d3.y + 5), 3)
        acad.model.AddText(p['p2']+"'", APoint(d4.x, d4.y + 5), 3)
        acad.model.AddDimRotated(APoint(0.0, 0.0), d1, APoint(-10, -p['front']/2), 1.5708)
        acad.model.AddDimAligned(d1, d2, APoint(d1.x, d1.y - 15))
        acad.model.AddDimAngular(d1, d2, APoint(30.0, -p['front']),APoint(d1.x + 20, d1.y - 5))
        if float(p.get('above', 0)) != 0.0:
            acad.model.AddDimRotated(APoint(0.0, 0.0), d3, APoint(-10, p['above']/2), 1.5708)

    draw_line(d1, d3, color=4, lw=-1)
    draw_line(d2, d4, color=4, lw=-1)

    acad.app.ZoomExtents()

def draw_line(p1, p2, color=7, lw=30):
    line = acad.model.AddLine(p1, p2)
    line.Color, line.Lineweight = color, lw

def add_label(text, pt, dx=2, dy=2):
    acad.model.AddText(text, APoint(pt.x + dx, pt.y + dy), 3)

# ============   MAIN   =============
print("-> Opening AutoCAD")
draw_projection()
print("<--- DONE --->")